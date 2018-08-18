from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

class JackAnalyzer:

    __slots__ = '_inputstream', '_outputstream', '_tokenizer', '_compilation_engine'

    def __init__(self, filepath):
        self._inputstream = filepath
        self._outputstream = filepath.replace(".jack", ".xml")
        self._tokenizer = JackTokenizer(input)

