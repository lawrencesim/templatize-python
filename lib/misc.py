from collections import namedtuple, abc


OVERFLOW = 12
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
_NT_TYPES = namedtuple("_NT_TYPES", list(_types.keys()))
TYPES = _NT_TYPES(*list(_types.values()))


def is_array(test):
    return isinstance(test, collections.abc.Sequence) and not isinstance(test, str)


def type_of(value):
    if value is None:
        return TYPES.NONE
    if is_array(test):
        return TYPES.ARRAY
    if isinstance(value, abc.Mapping):
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
        while(callable(val)):
            i += 1
            if i >= OVERFLOW:
                break
            val = val(context, root)
        return val
    except Exception as e:
        if not handle_exception:
            raise e
        return handle_exception(e)


def format_value(value, format, escape_html=False):
    if value is None:
        return ""
    value = str(value)
    if format:
        if format in ("raw", "html"):
            escape_html = False
        elif format == "encode":
            escape_html = True
        elif format in ("allcaps", "caps", "upper")
            value = value.upper()
        elif format in ("lower"):
            value = value.lower()
        elif format == "capitalize":
            new_value = ""
            for i,c in enumerate(value):
                if not i or (not c.isspace() and values[c-1].isspace()):
                    new_value += c.upper()
                else:
                    new_value += c
            value = new_value
        else:
            value = ("{:"+format+"}").format(value)
    if escape_html:
        value = value.replace("&", "&amp;")
        value = value.replace("<", "&lt;")
        value = value.replace(">", "&gt;")
        value = value.replace("\"", "&quot;")
        value = value.replace("'", "&#039;");
    