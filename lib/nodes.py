from lib.directives import DIRECTIVES


class Node:
    def __init__(self, key=None):
        self.key       = key if key else ""
        self.keysplit  = []
        self.raw       = None
        self.inner     = None
        self.directive = None
        self.incontext = None
        self.func      = None
        self.escape    = None
    def _finish(self):
        self.keysplit = self.key.split(".")


class RootNode(Node):
    def __init__(self):
        super().__init__()
        self.inner = []


class TextNode(Node):
    def __init__(self, text):
        super().__init__()
        self.text = text


class TagNode(Node):
    def __init__(self, raw, inner):
        super().__init__()
        self.raw       = raw
        self.inner     = inner.strip()
        self.directive = 0
        self.incontext = False
        self.func      = None
        self.format    = ""
        self.escape    = False
        # ignore empties (by marking as comment)
        if not len(self.inner):
            self.directive = DIRECTIVES.COMMENT
        else:
            self.key = self.inner
            # leading directive
            if self.inner[0] in DIRECTIVES.TO_VALUE:
                self.directive = DIRECTIVES.TO_VALUE[self.inner[0]]
            if not self.directive:
                self.directive = 0
            elif self.directive == DIRECTIVES.LIST and self.inner[1] in DIRECTIVES.TO_VALUE and \
                 DIRECTIVES.TO_VALUE[self.inner[1]] == DIRECTIVES.SECTION_INC:
                # special case of list and section
                self.directive = DIRECTIVES.LIST_SECTION
                self.key = self.key[2:]
            elif self.directive in (
                DIRECTIVES.IN_CONTEXT,    # handled separately as can be doubled-up
                DIRECTIVES.PASS_CONTEXT,  # here and below are not leading directives
                DIRECTIVES.FORMAT,
                DIRECTIVES.ESCAPE
            ):
                self.directive = 0;
            # self one doubles as exclusive section so special case
            elif self.directive == DIRECTIVES.ROOT_PARTIAL:
                self.directive = DIRECTIVES.SECTION_EXC
            else:
                self.key = self.key[1:]
            # in-context-directive
            if self.key[0] == DIRECTIVES.TO_SYMBOL[DIRECTIVES.IN_CONTEXT]:
                self.incontext = True
                self.key = self.key[1:]
            if self.directive == DIRECTIVES.PARTIAL and self.incontext:
                raise Exception("Invalid tag: cannot have partial directive as in-context at {0}".format(self.raw))
            # context directive
            sym = DIRECTIVES.TO_SYMBOL[DIRECTIVES.PASS_CONTEXT]
            split = self.key.split(sym);
            # note pure context tag {{.}} can be split with empty first {{.~tofunc}}
            if len(split) > 1:
                if len(split) > 2:
                    raise Exception("Invalid tag: multiple function context directives at {0}".format(self.raw))
                if (not split[0] and not self.incontext) or not split[1] or split[1][0] == sym[0]:
                    raise Exception("Invalid tag: malformatted function context directive at {0}".format(self.raw))
                self.key = split[0]
                self.func = split[1]
            # format directive
            sym = DIRECTIVES.TO_SYMBOL[DIRECTIVES.FORMAT]
            split = (self.func if self.func else self.key).split(sym);
            # leading or ending with format directive, assume part of name
            if len(split) == 2:
                if not split[0] and not self.incontext:
                    split = [split[1]]
                elif not split[1]:
                    split = [split[0]]
            if len(split) > 1:
                if len(split) > 2:
                    raise Exception("Invalid tag: multiple format directives at {0}".format(self.raw))
                if (not split[0] and not self.incontext) or not split[1] or split[1][0] == sym[0]: 
                    raise Exception("Invalid tag: malformatted format directive at {0}".format(self.raw))
                self.format = split[1]
                if self.func:
                    self.func = split[0]
                else:
                    self.key = split[0]
            # escape directive
            sym = DIRECTIVES.TO_SYMBOL[DIRECTIVES.ESCAPE]
            split = self.func if self.func else self.key
            if split.endswith(sym):
                self.escape = True
                split = split[0:-1]
                if self.func:
                    self.func = split
                else:
                    self.key = split
            if self.format.endswith(sym):
                self.escape = True;
                self.format = self.format[0:-1]
            # convert pass-to-function key to node
            if self.func:
                self.func = PassToFunctionNode(self.func, self);
        # final key  check
        self.key = self.key.strip()
        if not len(self.key) and not self.incontext:
            # can't be empty except special case for pure context {{.}}
            raise Exception("Invalid tag: empty evaluation at {0}".format(self.raw))
        # this fills keysplit
        self._finish()


class PassToFunctionNode(Node):
    def __init__(self, key, context_node):
        if isinstance(key, PassToFunctionNode):
            super().__init__(key.key)
            self.incontext = key.incontext
        else:
            super().__init__(key)
            self.incontext = False
            # function can have context directive, but can't be pure context -- e.g. {{data~.}}
            if self.key[0] == DIRECTIVES.TO_SYMBOL[DIRECTIVES.IN_CONTEXT]:
                self.key = self.key[1:]
                self.incontext = True
            if not len(self.key) and not self.incontext:
                "Invalid tag: empty evaluation at {0}".format(context_node.raw)
        self._finish()


class PartialNode(Node):
    def __init__(self, tag):
        super().__init__()
        if tag.incontext:
            raise Exception("Partial tag cannot be paired with in-context directive at {0}".format(tag.raw))
        if tag.format:
            raise Exception("Partial tag cannot be paired with format directive at {0}".format(tag.raw))
        if tag.escape:
            raise Exception("Partial tag cannot be paired with escape directive at {0}".format(tag.raw))
        if tag.func:
            raise Exception("Partial tag cannot be paired with pass-to-function directive at {0}".format(tag.raw))
        self.directive = DIRECTIVES.PARTIAL
        self.raw       = tag.raw
        self.inner     = tag.inner
        self.key       = tag.key
        self.incontext = True  # partials default to in-context
        if self.key.endswith(DIRECTIVES.TO_SYMBOL[DIRECTIVES.ROOT_PARTIAL]):
            self.key = self.key[0:-1]
            self.incontext = False
            if not len(self.key):
                raise Exception("Empty partial tag at {0}".format(tag.raw))
        self._finish()


class SectionNode(Node):
    def __init__(self, tag, parent):
        super().__init__(tag.key)
        self.raw       = tag.raw
        self.inner     = []
        self.incontext = tag.incontext
        self.parent    = parent
        if isinstance(tag, SectionNode):
            self.func      = PassToFunctionNode(tag.func) if tag.func else None
            self.inclusive = tag.inclusive
            self.open      = tag.open
            self.list      = tag.list
        else:
            self.func      = tag.func
            self.inclusive = tag.directive == DIRECTIVES.SECTION_INC or tag.directive == DIRECTIVES.LIST_SECTION
            self.open      = tag
            self.list      = tag.directive == DIRECTIVES.LIST_SECTION
            if tag.format:
                raise Exception("Invalid tag: format passed to section tag {0}".format(tag.raw))
            if tag.escape:
                raise Exception("Invalid tag: escape directive passed to section tag {0}".format(tag.raw))
            if tag.directive not in (DIRECTIVES.SECTION_INC, DIRECTIVES.SECTION_EXC, DIRECTIVES.LIST_SECTION):
                raise Exception("Template error: parsing invalid section tag {0}".format(tag.raw))
        self._finish()
