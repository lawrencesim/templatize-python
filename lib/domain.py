from lib.nodes import Node
from lib.misc import TYPES, type_of, evalf


class DynamicDomain:

    def __init__(self, domain):
        self.domain   = domain
        self.children = {}
        self.type     = self.domain.type

    def create(self, dkey, with_data, index):
        dykey = "<{0}:{1}>".format(index if index else 0, dkey)
        if dykey in self.children:
            return self.children[dykey]
        context = Domain(with_data, self.domain.fullkey, self.domain.parent)
        context.cache = {}  # disconnect cache for dynamic contexts
        self.children[dykey] = context
        return context

    def __len__(self):
        if self.type in (TYPES.NULL, TYPES.UNDEFINED):
            return 0
        if self.type == TYPES.ARRAY:
            return len(self.domain.data)
        return 1

    def get(self, index, on_func_error=None):
        data = self.domain.data[index] if self.domain.isrepeating else self.domain._eval(on_func_error)
        return self.create("", data, index)


class Domain:

    def __init__(self, data=None, fullkey=None, parent=None):
        self.fullkey       = fullkey if fullkey else ""
        self.prefix        = self.fullkey + "." if self.fullkey else self.fullkey
        self.prefixlen     = len(self.prefix.split(".")) - 1
        self.data          = data if data else {}
        self.function      = None
        self.type          = type_of(self.data)
        self.parent        = parent if parent else None
        self.root          = self.parent.root if self.parent and self.parent.root else self
        self.cache         = parent.cache if parent and parent.cache else {}
        self.children      = {".": self}
        self.isrepeating   = False
        self.dynamic       = DynamicDomain(self)
        #     'children': {}, 
        #     'length':   self.length_dynamic, 
        #     'get':      self.get_dynamic, 
        #     'create':   self.create_dynamic
        # };
        # function store reference to function, data is f() output but resolved whenever first called
        if self.type == TYPES.FUNCTION:
            self.function = self.data
            self.data = None
        # dynamic data that changes based on context (e.g. an array where items iterated with same tags)
        elif self.type == TYPES.ARRAY:
            self.isrepeating = True

    def reroot(self):
        return Domain(self.data)

    def _eval(self, on_func_error=None):
        if self.function and not self.data:
            self.data = evalf(self.function, self.parent.data, self.root.data, on_func_error)
            self.type = type_of(self.data)
            if self.type == TYPES.ARRAY:
                self.isrepeating = True
            else:
                self.cache[self.fullkey] = self
        return self.data

    # Get raw value (assumed called when already in inner-most context). For functions uses evaluated value.
    def value(self, on_func_error=None):
        return self._eval(on_func_error)

    # Get child data domain / subcontext. If function and first time, evaluates function till non-function 
    # type and changes type. If called in dynamic domain, return null.
    def get(self, key, on_func_error=None, skip_cache=False):
        if key and key != ".":
            fullkey = self.prefix + key
        else:
            fullkey = self.fullkey
            key = "."
        # functions render on first handle to resolve what data is
        self._eval(on_func_error)
        # check cache
        if not skip_cache and fullkey in self.cache:
            print(self.cache[fullkey])
            return self.cache[fullkey]
        # can't normal 'get' children of repeating sections (use getDynamic)
        if self.isrepeating:
            return None
        # get context or create if not yet existing
        if key in self.children:
            return self.children[key]
        if key not in self.data:
            return None
        subcontext = Domain(self.data[key], fullkey, self)
        self.cache[fullkey] = self.children[key] = subcontext
        return subcontext

    # Get dynamic length.
    # def length_dynamic(self):
    #     if self.type in (TYPES.NULL, TYPES.UNDEFINED):
    #         return 0
    #     if self.type == TYPES.ARRAY:
    #         return len(self.data)
    #     return 1

    # Get dynamic data domain with custom data. Must also supply unique key modifier.
    # Dynamic data domain acts as if in the same location as this domain (with same key and parent), but with
    # dynamic data that is different. Note that if search up to parent and back down, however, it cannot be 
    # re-found with same key. It is technically stored as a dynamic child of this domain.
    # def create_dynamic(self, dkey, with_data, index):
    #     dykey = "<{0}:{1}>".format(index if index else 0, dkey)
    #     if dykey in self.dynamic.children:
    #         return self.dynamic.children[dykey]
    #     context = Domain(with_data, self.fullkey, self.parent)
    #     context.cache = {}  # disconnect cache for dynamic contexts
    #     self.dynamic.children[dykey] = context
    #     return context

    # Get dynamic data domain by index. Used for repeating sections to dynamically load the domain of an 
    # array item. If not an array-type, simply loads the current data.
    # def get_dynamic(self, index, on_func_error=None):
    #     data = self.data[index] if self.isrepeating else self._eval(on_func_error)
    #     return self.create_dynamic("", data, index)

    # Check if node is in this context (lazy search, doesn't check if most specific).
    def incontext(self, fullkey_or_node):
        key = fullkey_or_node
        if isinstance(fullkey_or_node, Node):
            if fullkey_or_node.incontext:
                return True
            key = fullkey_or_node.key
        return key == self.fullkey or key.startswith(self.prefix)

    # Search for domain.
    def _search(self, fullkey, keysplit, on_func_error=None, bubble=False, atstart=False):
        # if start of search, try cache
        if atstart and fullkey in self.cache:
            return self.cache[fullkey]
        # if exactly at, return self
        if not len(keysplit) or self.fullkey == fullkey:
            return self;
        if bubble: 
            # reverse search condition when in context or at root (can always bubble out of dynamic domain)
            if not self.parent:
                return self._search(fullkey, keysplit, on_func_error)
            elif self.incontext(fullkey):
                # remove incontext prefix from fullkey before searching inside
                rmlen = 0;
                while len(keysplit) and ++rmlen < self.prefixlen:
                    rmlen += 1
                    keysplit.pop(0)
                return self._search(fullkey, keysplit, on_func_error)
            # continue bubbling (if exiting dynamic, reset 'atstart' to try parent's cache)
            return self.parent._search(fullkey, keysplit, on_func_error, True, self.isrepeating)
        # to handle names with periods in them (user-error by try to work with), append key parts till match
        key = "";
        for k, skey in enumerate(keysplit):
            key += skey
            subcontext = self.get(key, on_func_error, True);
            if subcontext:
                if subcontext == self:
                    return self  # special case when key="."
                return subcontext._search(fullkey, keysplit[k+1:], on_func_error)
            key += "."
        return None if len(keysplit) else self

    def search(self, node, on_func_error=None):
        # special case for naked context tags
        if not node.key and node.incontext:
            return self
        # try cache with full keys (note in-context nodes skip bubble)
        return self._search(node.key, node.keysplit[:], on_func_error, (not node.incontext), True)
