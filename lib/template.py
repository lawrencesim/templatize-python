from lib.nodes import RootNode, TextNode, TagNode, PartialNode, SectionNode
from lib.directives import DIRECTIVES


DEFAULT = {
    "delimiters": ["{{", "}}"]
}


class Template:

    def __init__(self, template, options=None):
        self.root  = RootNode()
        delimiters = DEFAULT["delimiters"] if not options or not options["delimiters"] else options.delimiters
        last       = 0
        search     = 0
        dopen      = 0
        start      = -1
        dclose     = -1
        current    = self.root
        nest       = 0
        raw        = None
        node       = None
        while True:
            # find opening delimiter
            dopen = template.find(delimiters[0], search)
            if dopen < 0:
                break
            start = dopen + len(delimiters[0])
            # find closing delimiter
            dclose = template.find(delimiters[1], search)
            if dclose < 0:
                break
            # update search position
            search = dclose + len(delimiters[1])
            # ignore escaped (remove directive character in template)
            if template[dopen-1] == "!":
                template = template[0:dopen-1] + template[dopen:]
                search -= 1
                continue
            # grab preceding content
            if dopen and dopen > last:
                current.inner.append(TextNode(template[last:dopen]))
            last = search
            # create node and handle
            node = TagNode(
                template[dopen:search], 
                template[start:dclose].strip()
            )
            # ignore comments
            if node.directive == DIRECTIVES.COMMENT:
                pass
            # handle sections
            elif node.directive == DIRECTIVES.SECTION_END:
                if isinstance(current, RootNode):
                    raise Exception("Invalid template: unpaired section close at {0}".format(node.raw))
                if current.open.key != node.key:
                    raise Exception("Invalid template: Invalid template: section conflict at {0} close before inner {1} closed".format(node.raw, current.open.raw))
                current = current.parent
                nest -= 1
            elif node.directive in (DIRECTIVES.LIST_SECTION, DIRECTIVES.SECTION_INC, DIRECTIVES.SECTION_EXC):
                section = SectionNode(node, current)
                current.inner.append(section)
                current = section
                nest += 1
            # convert partials
            elif node.directive == DIRECTIVES.PARTIAL:
                node = PartialNode(node)
                current.inner.append(node)
            else:
                current.inner.append(node)
        # push last text
        if last < len(template):
            current.inner.append(TextNode(template[search:]))
        # final error check
        if current != self.root:
            raise Exception("Invalid template: hanging open section for {0}".format(current.open.raw))
        