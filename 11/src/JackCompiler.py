from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from CompilationEngine import CompilationEngine
from VMWriter import VMWriter

import os


class JackCompiler:

    def __init__(self, input_path):
        self._tokenizer = JackTokenizer(input_path)
        self._compilation = CompilationEngine(self._tokenizer)
        self._vm_writer = VMWriter(input_path.replace(".jack", ".vm"))
        self._symbol_table = SymbolTable()
        self.class_name = os.path.splitext(os.path.basename(input_path))[0]

    def