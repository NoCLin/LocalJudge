class GlobalVar:
    var_dict = {}


def get(k, default=None):
    return GlobalVar.var_dict.get(k, default)


# noinspection PyShadowingBuiltins
def set(k, v):
    GlobalVar.var_dict[k] = v
