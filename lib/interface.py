from lib.nodes import RootNode, TextNode, PartialNode, SectionNode, Node
from lib.misc import TYPES, type_of, evalf, format_value, is_array
from lib.directives import DIRECTIVES, SYMBOLS
from lib.template import Template
from lib.domain import Domain
import json


DEFAULT = {
    "error_on_func_failure": False, 
    "eval_zero_as_true":     False, 
    "escape_all":            False, 
    "error_on_missing_tags": False
}


class Result:

    def __init__(self):
        self.fullkey     = ""
        self.isdynamic   = False
        self.isrepeating = False
        self.length      = 0
        self.node        = None
        self.value       = None
        self.func        = None

    def __len__(self):
        return self.length

    def get_domain(self):
        if self.isrepeating:
            if self.func:
                return self.node.dynamic.create(self.func.fullkey, self.value)
            return self.node
        if not self.isdynamic:
            return self.node
        return self.node.dynamic.create(self.func.fullkey, self.value)


class Interface:

    def __init__(self, template, options=None):
        self._parse_options(options)
        self._template            = template
        self._root                = None
        self._partials            = {}
        self._options             = {}
        self._errorHandler        = None
        self._spawn_error_handler = None

    @property
    def error_on_func_failure(self):
        return self._error_on_func_failure
    @property
    def eval_zero_as_true(self):
        return self._eval_zero_as_true
    @property
    def escape_all(self):
        return self._escape_all
    @property
    def error_on_missing_tags(self):
        return self._error_on_missing_tags

    @error_on_func_failure.setter
    def error_on_func_failure(self, to):
        if to is not None:
            self._error_on_func_failure = bool(to)
    @eval_zero_as_true.setter
    def eval_zero_as_true(self, to):
        if to is not None:
            self._eval_zero_as_true = bool(to)
    @escape_all.setter
    def escape_all(self, to):
        if to is not None:
            self._escape_all = bool(to)
    @error_on_missing_tags.setter
    def error_on_missing_tags(self, to):
        if to is not None:
            self._error_on_missing_tags = bool(to)

    def _parse_options(self, options=None):
        if not options:
            options = {}
        self.error_on_func_failure = options["error_on_func_failure"] if "error_on_func_failure" in options \
                                        else DEFAULT["error_on_func_failure"]
        self.eval_zero_as_true     = options["eval_zero_as_true" ] if "eval_zero_as_true" in options \
                                        else DEFAULT["eval_zero_as_true"]
        self.escape_all            = options["escape_all"] if "escape_all" in options \
                                        else DEFAULT["escape_all"]
        self.error_on_missing_tags = options["error_on_missing_tags"] if "error_on_missing_tags" in options \
                                        else DEFAULT["error_on_missing_tags"]
        # snapshot options
        self._options = {
            "error_on_func_failure": self.error_on_func_failure, 
            "eval_zero_as_true":     self.eval_zero_as_true, 
            "escape_all":            self.escape_all, 
            "error_on_missing_tags": self.error_on_missing_tags
        }

    def _missing_handler(self, key, throw_error=False):
        if throw_error or self._error_on_missing_tags:
            raise Exception("Render error: missing binding for {0}".format(key))
        return ""

    def _error_handler_inner(self, key, exception):
        if self.error_on_func_failure:
            raise exception
        print("Error evaluating bindings at {0}".format(key))
        print(exception)
        return ""

    def render(self, bindings, options=None):
        self._parse_options(options)
        if self.error_on_func_failure:
            self._spawn_error_handler = lambda key : lambda exception : self._error_handler_inner(key, exception)

        try:
            if isinstance(bindings, Domain):
                self._root = bindings.reroot()
            else:
                self._root = Domain(bindings)

            # map partials
            self._partials = {}
            if options and "partials" in options and options["partials"]:
                self._partials = options["partials"]
            for pkey, partial in self._partials.items():
                if isinstance(partial, str):
                    try:
                        self._partials[pkey] = Template(partial)
                    except Exception as e:
                        "Invalid partial template for '{0}'".format(pkey)
                        raise e
                elif not isinstance(partial, Template):
                    raise Exception("Invalid partial: must be instance of Template or template string ('{0}' is {1})".format(pkey, type(partial)))

            return self._render_inside_out(self._render_outside_in(self._template.root))

        finally:
            # clean up references and temporary variables
            self._root                = None
            self._partials            = {}
            self._spawn_error_handler = None

    def _process_context(self, node, domain, dynamics=None):
        on_func_error = self._spawn_error_handler(node.raw) if self._spawn_error_handler else None
        def search(snode):
            if not snode.incontext and dynamics and len(dynamics):
                for dy in reversed(dynamics):
                    if dy.incontext(snode.key):
                        return dy.search(snode, on_func_error)
            return domain.search(snode, on_func_error)

        result = Result()

        # get domain of node
        result.node = search(node)
        if not result.node:
            return None

        if not node.func:
            result.value     = result.node.value(on_func_error)
            result.isdynamic = result.isrepeating = result.node.isrepeating
            result.length    = len(result.node.dynamic)

        else:
            # get domain of function
            result.func = search(node.func)
            result.isdynamic = True
            if not result.func:
                raise Exception("Context passed to unresolved function at {0}".format(node.raw))
            if not result.func.function:
                raise Exception("Context passed to non-function at {0}".format(node.raw))

            result.value = evalf(
                result.func.function, 
                result.node.value(on_func_error), 
                self._root.data, 
                on_func_error
            )
            if is_array(result.value):
                result.isrepeating = True
                result.length = len(result.value)

        return result

    def _render_outside_in(self, root, domain=None, processed=None, unresolved=None):
        domain     = domain if domain else self._root
        processed  = processed if processed else RootNode()
        unresolved = unresolved if unresolved else []

        for node in root.inner:
            # skip comments (shouldn't exist but just in case)
            if node.directive == DIRECTIVES.COMMENT:
                continue

            # text doesn't need processing
            if isinstance(node, TextNode):
                processed.inner.append(node)
                continue

            # render partial as sub-render with passed data domain and duplicate options
            if isinstance(node, PartialNode):
                processed.inner.append(self._partial(node, domain))
                continue

            # handling nodes in an unresolved context, some exceptions for sections and lists
            if domain.isrepeating and (node.func and node.func.incontext or node.incontext):
                processed.inner.append(node)
                continue
            for_section = isinstance(node, SectionNode)
            check_node = not for_section and node.directive != DIRECTIVES.LIST
            if len(unresolved) and check_node or node.func:
                cant_resolve = False
                for u in unresolved:
                    if check_node and u.incontext(node.key):
                        cant_resolve = True
                    elif node.func and u.incontext(node.func.key):
                        cant_resolve = True
                if cant_resolve:
                    processed.inner.append(node)
                    continue

            # get data context -- if null, likely due to nesting into dynamic data, so defer processing
            context = self._process_context(node, domain)
            if context is None:
                processed.inner.append(node)
                continue

            # render sections (handler split out, but basically recurses here)
            if for_section:
                self._section(node, context, processed, unresolved)
                continue

            # render straight values unless it depends on dynamic context (those defer till 2nd round)
            processed.inner.append(self._render_value(node, context.value))

        return processed

    def _render_inside_out(self, root, domain=None, dynamics=None):
        domain   = domain if domain else self._root
        dynamics = dynamics if dynamics else []

        processed = []
        for node in root.inner:

            # only handle sections for this first outside-in loop
            if not isinstance(node, SectionNode):
                processed.append(node)
                continue

            # get context, missing here is either skip or exception thrown
            context = self._process_context(node, domain, dynamics)
            if context is None:
                self._missing_handler(node.raw)
                continue
            # convert to dynamic domain, if necessary
            use_domain = context.get_domain()

            # standard section bound to context within a dynamic data domain
            if not context.isrepeating:
                if self._display(node.inclusive, use_domain):
                    processed.append(self._render_inside_out(node, use_domain, dynamics))
                continue

            # only thing left is repeating sections
            pieces = []
            for i in range(context.length):
                dydom = use_domain.dynamic.get(i)
                dynamics.append(dydom)
                if self._display(True, dydom):
                    pieces.append(self._render_inside_out(node, dydom, dynamics))
                dynamics.pop(-1)
            # either just add nodes to processed or convert to grammatic list
            if not node.list:
                processed += pieces
            else:
                plen = len(pieces)
                if plen == 0:
                    pass
                elif plen == 1:
                    processed.append(pieces[0])
                elif plen == 2:
                    processed.append("{0} and {1}".format(pieces[0], pieces[1]))
                else:
                    last = pieces.pop(-1)
                    processed.append("{0}, and {1}".format(", ".join(pieces), last))

        # this part will run from inner-most out on all remaining nodes
        text = ""
        for node in processed:
            if isinstance(node, TextNode):
                text += node.text
            elif isinstance(node, str):
                text += node
            elif not isinstance(node, Node):
                text += str(node)
            else:
                context = self._process_context(node, domain, dynamics)
                if context is None:
                    text += self._missing_handler(node.raw)
                else:
                    text += self._render_value(node, context.value)
        return text

    def _section(self, node, context, processed, unresolved):
        # Repeating sections recurse inner content to process any non-dynamic referencing tags, but also add 
        # node to processing array for final processing in inside-out rendering.
        if context.isrepeating:
            if node.inclusive and context.length:
                # Copy section node and replace any in-context shortcuts with full path as it will be handled
                # later, potentially out of context.
                dynode = SectionNode(node, None)
                if dynode.incontext:
                    dynode.key = context.node.fullkey
                    dynode.incontext = False
                    dynode._finish()
                if dynode.func and dynode.func.incontext:
                    dynode.func.key = context.func.fullkey
                    dynode.func.incontext = False
                    dynode.func._finish()
                domain = context.get_domain()
                # Add to unresolved domains, recurse, pop unresolved domain, add to processing
                unresolved.append(domain)
                self._render_outside_in(node, domain, dynode, unresolved)
                unresolved.pop(-1)
                processed.inner.append(dynode)
        # Standard sections simple recurse inner content to render. Only thing is checking for creation of 
        # dynamic data context first.
        else:
            domain = context.get_domain()
            if self._display(node.inclusive, domain):
                self._render_outside_in(node, domain, processed, unresolved)

    def _display(self, inclusive, domain):
        display = domain.value()
        if domain.type == TYPES.OBJECT:
            _display = domain.get("_display")
            if _display is not None:
                return _display.value()
        elif domain.type == TYPES.ARRAY and not len(display):
            # discrepancy from javascript where empty arrays are still truthy
            display = True
        else:
            if isinstance(display, str):
                display = display.strip()
            elif isinstance(display, (int, float)):
                display = display if display != 0 else self.eval_zero_as_true
        return inclusive == bool(display)

    def _partial(self, node, context):
        if not self._partials[node.key]:
            if self.error_on_missing_tags:
                raise Exception("Render error: missing partial for {0}".format(node.key))
            print("Render error: missing partial for {0}".format(node.key))
            return ""
        try:
            return self._partials[node.key].render(
                context if node.incontext else self._root, 
                self._options
            )
        except Exception as e:
            print("Partial render error for {0}".format(node.key))
            print(e)
            return ""

    def _render_value(self, node, value):
        nformat = node.format
        vtype = type_of(value)
        if vtype <= TYPES.NULL:
            return ""
        # format list (unless not array, then normal handling)
        if node.directive == DIRECTIVES.LIST and vtype == TYPES.ARRAY:
            value = [
                str(vi) if is_array(vi) else 
                    format_value(vi, nformat, node.escape if node.escape else self.escape_all)
                for vi in value
            ]
            vlen = len(value)
            if vlen == 0:
                return ""
            if vlen == 1:
                return value[0]
            if vlen == 2:
                return "{0} and {1}".format(value[0], value[1])
            else:
                last = value.pop(-1)
                return "{0}, and {1}".format(", ".join(value), last)
        # other non-value types, convert to string
        if vtype == TYPES.ARRAY:
            value = str(value)
            nformat = False
        elif vtype == TYPES.OBJECT:
            value = json.dumps(value, default=str)
            nformat = False
        # final format and add
        return format_value(value, nformat, node.escape if node.escape is not None else self.escape_all)
