import collections, collections.abc


_types = {
    "UNDEFINED":  -1, 
    "NULL":       0, 
    "NONE":       0, 
    "VALUE":      1, 
    "STRING":     1, 
    "NUMBER":     1, 
    "ARRAY":      2, 
    "LIST":       2, 
    "OBJECT":     3, 
    "DICTIONARY": 3, 
    "FUNCTION":   4
}
_NT_types = collections.namedtuple("_NT_TYPES", list(_types.keys()))

OVERFLOW = 12
TYPES = _NT_types(*list(_types.values()))

del _types, _NT_types


def is_array(test):
    return isinstance(test, collections.abc.Sequence) and not isinstance(test, str)


def type_of(value):
    if value is None:
        return TYPES.NONE
    if is_array(value):
        return TYPES.ARRAY
    if isinstance(value, collections.abc.Mapping):
        return TYPES.DICTIONARY
    if callable(value):
        return TYPES.FUNCTION
    return TYPES.VALUE


def evalf(func, context, root, handle_exception=None):
    if not context:
        context = {}
    try:
        val = func
        i = 0
        while callable(val):
            i += 1
            if i >= OVERFLOW:
                break
            val = val(context, root)
        return val
    except Exception as e:
        if not handle_exception:
            raise e
        return handle_exception(e)


def format_value(value, format_op, escape_html=False):
    if value is None:
        return ""
    if format_op:
        if format_op in ("raw", "html"):
            value = str(value)
            escape_html = False
        elif format_op == "encode":
            value = str(value)
            escape_html = True
        elif format_op in ("allcaps", "caps", "upper"):
            value = str(value).upper()
        elif format_op in ("lower",):
            value = str(value).lower()
        elif format_op == "capitalize":
            value = str(value)
            new_value = ""
            for i, c in enumerate(value):
                if not i or (not c.isspace() and value[i-1].isspace()):
                    new_value += c.upper()
                else:
                    new_value += c
            value = new_value
        else:
            if format_op[0] == "$":
                format_op = "${0:"+format_op[1:]+"}"
            else:
                format_op = "{0:"+format_op+"}"
            value = format_op.format(value)
    else:
        value = str(value)
    if escape_html:
        value = value.replace("&", "&amp;")   \
                     .replace("<", "&lt;")    \
                     .replace(">", "&gt;")    \
                     .replace("\"", "&quot;") \
                     .replace("'", "&#039;")
    return value
    