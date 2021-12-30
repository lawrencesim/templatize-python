from collections import namedtuple


_symbols = {
    "COMMENT":      "!", 
    "LIST":         "&", 
    "LIST_SECTION": "&#", 
    "SECTION_INC":  "#", 
    "SECTION_EXC":  "^", 
    "SECTION_END":  "/", 
    "PARTIALS":     ">", 
    "ROOT_PARTIAL": "^", 
    "IN_CONTEXT":   ".", 
    "PASS_CONTEXT": "->", 
    "FORMAT":       "::", 
    "ESCAPE":       ";"
}
_symbol_nums = {}
for i,name in enumerate(list(_symbols.keys())):
    symbol = _symbols[name]
    _symbol_nums[symbol] = i + 1

_NT_SYM = namedtuple("_NT_SYM", list(_symbols.keys()))
_NT_DIR = namedtuple("_NT_DIR", list(_symbols.keys())+["TO_SYMBOL", "TO_VALUE"])
               # name to symbol
_NT_DIR_VALS = list(_symbols.values()) + [
    # value to symbol
    tuple([None] + list(_symbol_nums.keys())), 
    # symbol to values
    _symbol_nums
]

SYMBOLS = _NT_SYM(*list(_symbols.values()))
DIRECTIVES = _NT_DIR(*_NT_DIR_VALS)
