class SymbolTable:

    class _Symbol:  # light weight symbol class

        __slots__ = 'type', 'kind', 'id'

        # kind is type of variable the compiler interprets it: static, field, var, arg
        # type is class/type does variable belong to like int, char, boolean or Class
        def __init__(self, type, kind, id):
            self.type = type
            self.kind = kind
            self.id = id

    def __init__(self):
        self._counters = {
            "static": 0,
            "field": 0,
            "argument": 0,
            "var": 0,
        }
        self._class_scope = {}
        self._method_scope = {}

    def start_subroutine(self):
        self._method_scope = {}
        self._counters["argument"] = 0
        self._counters["var"] = 0

    def define(self, name, type, kind):
        if kind in ["static", "field"]:
            self._class_scope[name] = SymbolTable._Symbol(type, kind, self._counters[kind])
        else:  # handle ARG and VAR
            self._method_scope[name] = SymbolTable._Symbol(type, kind, self._counters[kind])
        self._counters[kind] += 1

    def var_count(self, kind):
        return self._counters[kind]

    def kind_of(self, name):
        kind_value = self._method_scope.get(name, None)
        if not kind_value:
            kind_value = self._class_scope.get(name, None)

        if kind_value:
            return kind_value.kind
        else:
            return None

    def type_of(self, name):
        kind_value = self._method_scope.get(name, None)
        if not kind_value:
            kind_value = self._class_scope.get(name, None)

        if kind_value:
            return kind_value.type
        else:
            return None

    def index_of(self, name):
        index = self._method_scope.get(name, None)
        if not index:
            index = self._class_scope.get(name, None)

        if index:
            return index.id
        else:
            return None
