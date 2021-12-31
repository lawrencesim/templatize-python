from collections import namedtuple


_symbols = {
    "COMMENT":      "!", 
    "LIST":         "&", 
    "LIST_SECTION": "&#", 
    "SECTION_INC":  "#", 
    "SECTION_EXC":  "^", 
    "SECTION_END":  "/", 
    "PARTIAL":      ">", 
    "ROOT_PARTIAL": "^", 
    "IN_CONTEXT":   ".", 
    "PASS_CONTEXT": "->", 
    "FORMAT":       "::", 
    "ESCAPE":       ";"
}
_symbol_names    = list(_symbols.keys())
_symbol_chars    = [_symbols[sn] for sn in _symbol_names]
_symbol_nums     = list(range(1, len(_symbol_names)+1))
_uq_symbol_chars = list(set(_symbol_chars))
_uq_symbol_map   = {}
for sc in _uq_symbol_chars:
    _uq_symbol_map[sc] = _symbol_nums[_symbol_chars.index(sc)]

_NT_symbols = namedtuple("_NT_SYM", _symbol_names)
SYMBOLS = _NT_symbols(*_symbol_chars)

_NT_directives = namedtuple("_NT_DIR", _symbol_names+["TO_SYMBOL", "TO_VALUE"])
DIRECTIVES = _NT_directives(*(
    _symbol_nums +             # symbol names to values (named tuple)
    [ ([None]+_symbol_chars),  # values to symbols (simple list)
      _uq_symbol_map ]         # symbols to values (dictionary)
))

del _NT_directives, _NT_symbols, _uq_symbol_chars, _uq_symbol_map, _symbol_names, _symbol_chars, _symbol_nums, _symbols
