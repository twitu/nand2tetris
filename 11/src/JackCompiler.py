from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

import os
import sys


class JackCompiler:

    def __init__(self, file_path):
        self._tokenizer = JackTokenizer(file_path)
        self._vm_writer = VMWriter(file_path.replace(".jack", "Compiled.vm"))
        self._symbol_table = SymbolTable()
        self.class_name = ""
        self.label_value = 1
        self.compile_class()

    def compile_class(self):
        self._tokenizer.next()  # ignore class
        self.class_name = self._tokenizer.next()
        self._tokenizer.next()  # ignore opening brackets

        while self._tokenizer.next() in ("static", "field"):
            self.compile_class_var_dec()
        else:
            self._tokenizer.go_back()

        while self._tokenizer.next() in ("constructor", "method", "function"):
            self.compile_subroutine()

    def compile_class_var_dec(self):
        var_kind = self._tokenizer.return_token_value()
        var_type = self._tokenizer.next()

        while True:
            self._tokenizer.next()
            var_name = self._tokenizer.return_token_value()
            self._symbol_table.define(var_name, var_type, var_kind)
            if self._tokenizer.next() == ';':
                break

    def compile_subroutine(self):
        self._symbol_table.start_subroutine()
        subroutine_type = self._tokenizer.return_token_value()

        self._tokenizer.next()  # ignore return type
        subroutine_name = self._tokenizer.next()

        # create mapping for "this" in symbol table
        # method is implicitly passed "this"
        if subroutine_type == "method":
            self._symbol_table.define("this", self.class_name, "argument")

        self._tokenizer.next()  # ignore '('
        self.compile_parameter_list()
        self._tokenizer.next()  # ignore ')'

        self._tokenizer.next()  # ignore '{'
        while self._tokenizer.next() == "var":  # var declarations
            self.compile_var_dec()
        else:
            self._tokenizer.go_back()

        self._vm_writer.write_function(self.class_name + "." + subroutine_name, self._symbol_table.var_count("var"))

        # TODO: handle constructor inside constructor as in SquareGame.new()
        if subroutine_type == "constructor":
            # allocate memory equal to number of field variables
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, self._symbol_table.var_count("field"))
            self._vm_writer.write_call("Memory.alloc", 1)
            # store pointer to new memory block as this (pointer 0)
            self._vm_writer.write_pop(VMWriter.POINTER_SEGMENT, 0)

        if subroutine_type == "method":
            self._vm_writer.write_push(VMWriter.ARG_SEGMENT, 0)  # implicit this pointer
            self._vm_writer.write_pop(VMWriter.POINTER_SEGMENT, 0)  # write to this of current scope
            for i in range(1, self._symbol_table.var_count("argument")):
                self._vm_writer.write_push(VMWriter.ARG_SEGMENT, i)
                self._vm_writer.write_pop(VMWriter.THIS_SEGMENT, i - 1)

        self.compile_statements()
        self._tokenizer.next()  # ignore closing '}' brackets

    def compile_parameter_list(self):
        if self._tokenizer.next() == ')':
            self._tokenizer.go_back()
            return
        else:
            self._tokenizer.go_back()
            parameter_type = self._tokenizer.next()
            parameter_name = self._tokenizer.next()
            self._symbol_table.define(parameter_name, parameter_type, "argument")

        while self._tokenizer.next() != ')':
            parameter_type = self._tokenizer.next()
            parameter_name = self._tokenizer.next()
            self._symbol_table.define(parameter_name, parameter_type, "argument")
        else:
            self._tokenizer.go_back()

    def compile_var_dec(self):
        var_kind = self._tokenizer.return_token_value()
        self._tokenizer.next()
        var_type = self._tokenizer.return_token_value()

        while self._tokenizer.next() != ';':
            var_name = self._tokenizer.return_token_value()
            self._symbol_table.define(var_name, var_type, var_kind)

    def compile_statements(self):
        while self._tokenizer.next() != "}":
            token_value = self._tokenizer.return_token_value()
            if token_value == "let":
                self.compile_let()
            elif token_value == "if":
                self.compile_if()
            elif token_value == "while":
                self.compile_while()
            elif token_value == "do":
                self.compile_do()
            elif token_value == "return":
                self.compile_return()

        self._tokenizer.go_back()

    def compile_let(self):
        name = self._tokenizer.next()
        index, kind = self._symbol_table.index_of(name), self._symbol_table.kind_of(name)
        array_access = False

        if self._tokenizer.next() == "[":
            if kind == "field":
                self._vm_writer.write_push(VMWriter.THIS_SEGMENT, index)
            else:
                self._vm_writer.write_push(kind, index)
            self.compile_expression()  # evaluated expression value at SP
            self._vm_writer.write_arithmetic("add")  # SP contains memory address array + base
            self._tokenizer.next()  # ignore ']'
            array_access = True
        else:
            self._tokenizer.go_back()

        self._tokenizer.next()  # ignore '='
        self.compile_expression()
        self._tokenizer.next()  # ignore ';'

        # evaluate expression and then pop value to variable on right side of assignment
        if array_access:
            self._vm_writer.write_pop(VMWriter.TEMP_SEGMENT, 0)  # pop expression value to temp register
            self._vm_writer.write_pop(VMWriter.POINTER_SEGMENT, 1)  # put array index address in THAT
            self._vm_writer.write_push(VMWriter.TEMP_SEGMENT, 0)  # re insert expression value on stack
            self._vm_writer.write_pop(VMWriter.THAT_SEGMENT, 0)  # pop expression value to array index
        else:
            self._vm_writer.write_pop(kind, index)  # pop evaluated expression to appropriate segment and index

    def compile_if(self):
        self._tokenizer.next()  # ignore '('
        self.compile_expression()
        self._vm_writer.write_arithmetic("~")
        self._vm_writer.write_if(self.label_value)
        self._tokenizer.next()  # ignore ')'

        self._tokenizer.next()  # ignore '{'
        self.compile_statements()  # if statements
        self._tokenizer.next()  # ignore '}'

        if self._tokenizer.next() == "else":
            self._tokenizer.next()  # ignore '{'
            self._vm_writer.write_goto(self.label_value + 1)
            self._vm_writer.write_label(self.label_value)
            self.compile_statements()  # if statements
            self._vm_writer.write_label(self.label_value + 1)  # skip over if when false statements
            self._tokenizer.next()  # ignore '}'
        else:
            self._tokenizer.go_back()
            self._vm_writer.write_label(self.label_value)

        self.label_value += 2

    def compile_while(self):
        self._tokenizer.next()  # ignore '('
        self._vm_writer.write_label(self.label_value)
        self.compile_expression()
        self._vm_writer.write_arithmetic("~")
        self._vm_writer.write_if(self.label_value + 1)
        self._tokenizer.next()  # ignore ')'

        self._tokenizer.next()  # ignore '{'
        self.compile_statements()
        self._vm_writer.write_goto(self.label_value)
        self._vm_writer.write_label(self.label_value + 1)
        self.label_value += 2
        self._tokenizer.next()  # ignore '}'

    def compile_do(self):
        self.compile_subroutine_call()
        self._vm_writer.write_pop(VMWriter.TEMP_SEGMENT, 0)  # discard popped value
        self._tokenizer.next()  # ignore ';'

    def compile_return(self):
        if self._tokenizer.next() == ";":
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, 0)  # void functions should return 0
        else:
            self._tokenizer.go_back()
            self.compile_expression()
            self._tokenizer.next()  # ignore ';'

        self._vm_writer.write_return()

    def compile_subroutine_call(self, sub_name=None):
        # if sub routine name is not given get next token
        # sub routine name will be given when called from compile_term
        if not sub_name:
            sub_name = self._tokenizer.next()

        # check if class function or method call
        args = 0
        if self._tokenizer.next() == '.':
            callee_name = sub_name
            sub_name = self._tokenizer.next()

            kind = self._symbol_table.kind_of(callee_name)
            if kind is None:  # function call of the form Math.multiply()
                name = callee_name + "." + sub_name
            else:  # method call of the form object.draw(this, ...)
                name = self._symbol_table.type_of(callee_name) + "." + sub_name
                self._vm_writer.write_push(kind, self._symbol_table.index_of(callee_name))
                args = 1
        else:  # implicit method call, push this as first argument
            self._tokenizer.go_back()
            name = self.class_name + "." + sub_name
            self._vm_writer.write_push(VMWriter.POINTER_SEGMENT, 0)
            args = 1

        self._tokenizer.next()  # ignore '('
        args += self.compile_expression_list()
        self._tokenizer.next()  # ignore ')'

        self._vm_writer.write_call(name, args)

    def compile_expression_list(self):
        args_count = 0

        if self._tokenizer.next() == ')':
            self._tokenizer.go_back()
            return args_count
        else:
            self._tokenizer.go_back()
            self.compile_expression()
            args_count += 1

        while self._tokenizer.next() != ')':
            self.compile_expression()
            args_count += 1
        self._tokenizer.go_back()
        return args_count

    def compile_expression(self):
        self.compile_term()

        while True:
            op = self._tokenizer.next()  # token is an op
            if op in [")", "]", ",", ";"]:  # expression termination characters
                self._tokenizer.go_back()
                break

            self.compile_term()
            if op == "/":
                self._vm_writer.write_call("Math.divide()", 2)
            elif op == "*":
                self._vm_writer.write_call("Math.multiply()", 2)
            else:
                self._vm_writer.write_arithmetic(op)

    def compile_term(self):
        self._tokenizer.next()
        token_type = self._tokenizer.token_type()
        token_value = self._tokenizer.return_token_value()
        if token_type == JackTokenizer.INT_CONST_TOKEN:
            self.compile_integer(token_value)
        elif token_type == JackTokenizer.STRING_CONST_TOKEN:
            self.compile_string(token_value)
        elif token_type == JackTokenizer.KEYWORD_TOKEN:  # only true, false, null and this
            self.compile_keyword(token_value)
        elif token_type == JackTokenizer.IDENTIFIER_TOKEN:  # subroutine or variables or array accesses
            if self._tokenizer.next() in ["(", "."]:
                self._tokenizer.go_back()
                self.compile_subroutine_call(token_value)
            else:
                self._tokenizer.go_back()
                self.compile_var_name(token_value)
        elif token_value == "(":
            self.compile_expression()
            self._tokenizer.next()  # ignore ')'
        elif token_type == JackTokenizer.SYMBOL_TOKEN:  # unary ops
            if token_value in ["-", "~"]:
                self.compile_term()
                self._vm_writer.write_arithmetic(token_value)
        else:
            exit("Invalid term")

    def compile_string(self, string):
        length = len(string)
        self._vm_writer.write_push(VMWriter.CONST_SEGMENT, length)
        self._vm_writer.write_call("String.new", 1)  # returns a new string pointer at SP

        for i in range(length):
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, ord(string[i]))
            self._vm_writer.write_function("String.appendChar", 1)  # append characters one by one to String at SP

    def compile_integer(self, value):
        self._vm_writer.write_push(VMWriter.CONST_SEGMENT, value)

    def compile_keyword(self, keyword):
        if keyword == "true":
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, 0)
            self._vm_writer.write_arithmetic("!")
        elif keyword == "this":
            self._vm_writer.write_push(VMWriter.POINTER_SEGMENT, 0)
        else:  # false and null
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, 0)

    def compile_var_name(self, name):
        index, kind = self._symbol_table.index_of(name), self._symbol_table.kind_of(name)

        if kind:  # index can be 0, so checking kind if symbol exists
            if kind == "field":
                self._vm_writer.write_push(VMWriter.THIS_SEGMENT, index)
            else:
                self._vm_writer.write_push(kind, index)
        else:
            exit("access to undefined variable")

        # evaluate array access
        if self._tokenizer.next() == "[":
            self.compile_expression()  # evaluated expression value at SP
            self._tokenizer.next()  # ignore '['
            self._vm_writer.write_arithmetic("+")
            self._vm_writer.write_pop(VMWriter.POINTER_SEGMENT, 1)  # pop array + base to THAT
            self._vm_writer.write_push(VMWriter.THAT_SEGMENT, 0)  # access [array + base] through THAT
        else:
            self._tokenizer.go_back()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError("Please give a file/directory path as argument")

    input_path = sys.argv[1]
    if os.path.isfile(input_path) and input_path.endswith(".jack"):
        jack_compiler = JackCompiler(input_path)
    elif os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.endswith(".jack"):
                jack_compiler = JackCompiler(os.path.join(input_path, file))
    else:
        raise ValueError("incorrect path given")
