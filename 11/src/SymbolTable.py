class SymbolTable:

    class _Symbol:  # light weight symbol class

        __slots__ = '_type', '_kind', '_id'

        def __init__(self, type, kind, id):
            self._type = type
            self._kind = kind
            self._id = id

    def __init__(self):
        self._counters = {
            "STATIC": 0,
            "FINAL": 0,
            "ARG": 0,
            "VAR": 0,
        }
        self._class_scope = {}
        self._method_scope = {}

    def start_subroutine(self):
        self._method_scope = {}
        self._counters["ARG"] = 0
        self._counters["VAR"] = 0

    def define(self, name, type, kind):
        if kind in ["STATIC", "FINAL"]:
            self._class_scope[name] = SymbolTable._Symbol(type, kind, self._counters[kind])
        else:  # handle ARG and VAR
            self._method_scope[name] = SymbolTable._Symbol(type, kind, self._counters[kind])
        self._counters[kind] += 1

    def var_count(self, kind):
        return self._counters[kind]

    def kind_of(self, name):
        kind_value = self._method_scope.get(name, default=None)
        if not kind_value:
            kind_value = self._class_scope.get(name, default=None)

        if kind_value:
            return kind_value._kind
        else:
            return None

    def index_of(self, name):
        index = self._method_scope.get(name, default=None)

        if not index:
            index = self._class_scope.get(name, default=None)
        return index._id - 1
