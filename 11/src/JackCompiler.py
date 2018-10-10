from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

import os
import sys


class JackCompiler:  # TODO: handle constructor inside constructor, get rid of advance function

    def __init__(self, input_path):
        self._tokenizer = JackTokenizer(input_path)
        self._vm_writer = VMWriter(input_path.replace(".jack", "Compiled.vm"))
        self._symbol_table = SymbolTable()
        self.class_name = ""
        self.label_value = 1
        self.compile_class()

    def advance(self, terminate_token=(), terminate_token_type=(), count=-1):
        # advances and prints terminals until it encounters termination character
        # also can specify number of tokens to print
        # by default it will keep tokenizing until terminating character
        while count != 0 and self._tokenizer.next():
            token_type = self._tokenizer.token_literal_name[self._tokenizer.token_type()]
            token = self._tokenizer.return_token_value()
            count -= 1
            # appends termination character string to xml output
            if token in terminate_token or token_type in terminate_token_type:
                # finishes on finding termination token or token_type
                return

    def compile_class(self):
        self.advance(terminate_token_type=("identifier",))
        self.class_name = self._tokenizer.return_token_value()
        self._tokenizer.next()  # skip opening bracket "{"
        while self._tokenizer.next() and self._tokenizer.return_token_value() in ["static", "field"]:
            self.class_compile_var_dec()
        else:
            self._tokenizer.go_back()

        while self._tokenizer.next() and self._tokenizer.return_token_value() in \
                ["constructor", "function", "method"]:
            self.compile_subroutine()
        else:
            if self._tokenizer.return_token_value() == "}":
                return
            else:
                self.error("class closing bracket")

    def class_compile_var_dec(self):
        var_kind = self._tokenizer.return_token_value()

        if self._tokenizer.next() and self._tokenizer.token_type() == JackTokenizer.KEYWORD_TOKEN:
            var_type = self._tokenizer.return_token_value()

            while self._tokenizer.next() and self._tokenizer.return_token_value() != ";":
                if self._tokenizer.token_type() == JackTokenizer.IDENTIFIER_TOKEN:
                    var_name = self._tokenizer.return_token_value()
                    self._symbol_table.define(var_name, var_type, var_kind)

    def compile_subroutine(self):
        self._symbol_table.start_subroutine()
        subroutine_type = self._tokenizer.return_token_value()

        # skip tokens till parameter call declaration
        self._tokenizer.next()  # skip return type
        if self._tokenizer.next():
            subroutine_name = self._tokenizer.return_token_value()
        else:
            self.error("subroutine declaration")

        if subroutine_type == "method":
            self._symbol_table.define("this", self.class_name,
                                      VMWriter.ARG_SEGMENT)  # this is a dummy written to store "this" in arg 0

        if self._tokenizer.next() and self._tokenizer.return_token_value() == "(":
            self.compile_parameter_list()

        if self._tokenizer.next() and self._tokenizer.return_token_value() == "{":  # enter body
            while self._tokenizer.next() and self._tokenizer.return_token_value() == "var":  # var declarations
                self.class_compile_var_dec()

        self._vm_writer.write_function(self.class_name + "." + subroutine_name, self._symbol_table.var_count("var"))

        if subroutine_type == "constructor":
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, self._symbol_table.var_count("field"))
            self._vm_writer.write_call("Memory.alloc", 1)
            self._vm_writer.write_pop(VMWriter.POINTER_SEGMENT, 0)
            for i in range(self._symbol_table.var_count("arg")):
                self._vm_writer.write_push(VMWriter.ARG_SEGMENT, i)
                self._vm_writer.write_pop(VMWriter.THIS_SEGMENT, i)

        if subroutine_type == "method":
            self._vm_writer.write_push(VMWriter.ARG_SEGMENT, 0)  # implicit this pointer
            self._vm_writer.write_pop(VMWriter.POINTER_SEGMENT, 0)  # write to this of current scope
            for i in range (1, self._symbol_table.var_count("arg")):
                self._vm_writer.write_push(VMWriter.ARG_SEGMENT, i)
                self._vm_writer.write_pop(VMWriter.THIS_SEGMENT, i - 1)

        self.compile_statements()
        if self._tokenizer.return_token_value() != "}":
            self.error("subroutine statements closing bracket")
        else:
            self.error("subroutine statements")

    def compile_parameter_list(self):
        while True:
            type = self._tokenizer.next()
            name = self._tokenizer.next()
            self._symbol_table.define(name, type, "arg")
            delimiter = self._tokenizer.next()
            if delimiter == ",":
                continue
            elif delimiter == ")":
                return
            else:
                self.error("subroutine parameter")

    def compile_subroutine_call(self, name=None):
        if not name:
            if self._tokenizer.next() and self._tokenizer.token_type() == JackTokenizer.IDENTIFIER_TOKEN:
                name = self._tokenizer.return_token_value()
                self._tokenizer.next()

        # at this point tokenizer points to token after subroutine name that could be "(" or "."
        if self._tokenizer.return_token_value() == ".":
            caller = name
            if self._tokenizer.next():
                name = self._tokenizer.return_token_value()
                self._tokenizer.next()

            kind = self._symbol_table.kind_of(caller)
            if kind is None:  # function call of the form Math.multiply()
                name = caller + "." + name
            else:  # method call push object reference as first argument
                name = self.class_name + "." + name
                self._vm_writer.write_push(kind, self._symbol_table.index_of(caller))
        else:  # implicit method call, push this as first argument
            name = self.class_name + "." + name
            self._vm_writer.write_push(VMWriter.POINTER_SEGMENT, 0)

        # at this point tokenizer should point to opening brackets
        args = 0
        if self._tokenizer.return_token_value() == "(":
            args = self.compile_expression_list()
        else:
            self.error("Incorrect method call")

        self._vm_writer.write_call(name, args)

    def compile_statements(self):
        self._tokenizer.go_back()
        while self._tokenizer.next() and self._tokenizer.return_token_value() != "}":
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
            else:
                self.error("statements not defined properly")

    def compile_return(self):
        if self._tokenizer.next() and self._tokenizer.return_token_value() != ";":
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, 0)  # void functions should return 0
        else:
            self.compile_expression()
        self._vm_writer.write_return()

    def compile_do(self):
        self.compile_subroutine_call()
        self._vm_writer.write_pop(VMWriter.TEMP_SEGMENT, 0)  # discard popped value
        if self._tokenizer.next() and self._tokenizer.return_token_value() == ";":
            pass
        else:
            self.error("incorrect do statement")

    def compile_while(self):
        if self._tokenizer.next() and self._tokenizer.return_token_value() == "(":
            self._vm_writer.write_label(self.label_value)
            self.compile_expression()
            self._vm_writer.write_if(self.label_value + 1)
        else:
            self.error("while statement")

        if self._tokenizer.next() and self._tokenizer.return_token_value() == "{":
            self.compile_statements()
            self._vm_writer.write_goto(self.label_value)
        else:
            self.error("while statement")
        self._vm_writer.write_label(self.label_value + 1)
        self.label_value += 2

    def compile_if(self):
        if self._tokenizer.next() and self._tokenizer.return_token_value() == "(":
            self.compile_expression()
        self._vm_writer.write_if(self.label_value)

        if self._tokenizer.next() and self._tokenizer.return_token_value() == "{":
            self._vm_writer.write_goto(self.label_value + 1)
            self.compile_statements()  # else statements

        if self._tokenizer.next() and self._tokenizer.return_token_value() == "else":
            if self._tokenizer.next() and self._tokenizer.return_token_value() == "{":
                self._vm_writer.write_label(self.label_value)
                self.compile_statements()  # if statements
                self._vm_writer.write_label(self.label_value + 1)  # skip over if when false statements
            else:
                self.error("if else error")
        else:
            self._tokenizer.go_back()
            self._vm_writer.write_label(self.label_value)

        self.label_value += 2

    def compile_let(self):
        if self._tokenizer.next() and self._tokenizer.token_type() == JackTokenizer.IDENTIFIER_TOKEN:
            name = self._tokenizer.return_token_value()
            index, kind = self._symbol_table.index_of(name), self._symbol_table.kind_of(name)
            array_access = False

            if self._tokenizer.next() and self._tokenizer.return_token_value() == "[":
                if index and kind:
                    if kind == "field":
                        self._vm_writer.write_push(VMWriter.THIS_SEGMENT, index)
                    else:
                        self._vm_writer.write_push(kind, index)
                else:
                    self.error("variable not declared properly")
                self.compile_expression()  # evaluated expression value at SP
                self._vm_writer.write_arithmetic("add")  # SP contains memory address array + base
                array_access = True
            else:
                self._tokenizer.go_back()

            if self._tokenizer.next() and self._tokenizer.return_token_value() == "=":
                self._tokenizer.next()
                self.compile_expression()

                # evaluate expression and then pop value to variable on right side of assignment
                if array_access:
                    self._vm_writer.write_pop(VMWriter.TEMP_SEGMENT, 0)  # pop expression value to temp register
                    self._vm_writer.write_pop(VMWriter.POINTER_SEGMENT, 1)  # put array index address in THAT
                    self._vm_writer.write_push(VMWriter.TEMP_SEGMENT, 0)  # re insert expression value on stack
                    self._vm_writer.write_pop(VMWriter.THAT_SEGMENT, 0)  # pop expression value to array index
                else:
                    if kind:  # index can be 0, so check only kind
                        self._vm_writer.write_pop(kind, index)
                    else:
                        self.error("variable not declared properly")
        else:
            self.error("variable not declared properly")

    def compile_expression_list(self):
        if self._tokenizer.next() and self._tokenizer.return_token_value() == ")":
            return 0
        else:
            self._tokenizer.go_back()

        count = 1
        self.compile_expression()

        while self._tokenizer.return_token_value() == ",":
            count += 1
            self.compile_expression()

        if self._tokenizer.return_token_value() != ")":
            self.error("expression list termination bracket missing")
        else:
            return count

    def compile_expression(self):
        self.compile_term()

        while self._tokenizer.next():
            token_type = self._tokenizer.token_type()
            token_value = self._tokenizer.return_token_value()
            if token_value in [")", "]", ",", ";"]:  # expression termination characters
                break

            if token_type == JackTokenizer.SYMBOL_TOKEN:  # compile op term and then compile term
                op = self._tokenizer.return_token_value()
                if op == "/":
                    if self._tokenizer.next(): self.compile_term()
                    self._vm_writer.write_call("Math.divide()", 2)
                elif op == "*":
                    if self._tokenizer.next(): self.compile_term()
                    self._vm_writer.write_call("Math.multiply()", 2)
                else:
                    self._vm_writer.write_arithmetic(op)
            else:
                self.error("OP missing")

            if self._tokenizer.next(): self.compile_term()

    def compile_term(self):
        token_type = self._tokenizer.token_type()
        token_value = self._tokenizer.return_token_value()
        if token_type == JackTokenizer.INT_CONST_TOKEN:
            self.compile_integer()
        elif token_type == JackTokenizer.STRING_CONST_TOKEN:
            self.compile_string()
        elif token_type == JackTokenizer.KEYWORD_TOKEN:  # only true, false, null and this
            self.compile_keyword()
        elif token_type == JackTokenizer.IDENTIFIER_TOKEN:  # subroutine or variables
            if self._tokenizer.next() and self._tokenizer.return_token_value() in ["(", "."]:
                self.compile_subroutine_call(token_value)
            else:
                self.compile_var_name(token_value)
        elif token_type == JackTokenizer.SYMBOL_TOKEN:  # unary ops
            if token_value in ["-", "~"]:
                self._vm_writer.write_arithmetic(token_value)
                self.compile_term()
            else:
                self.error("Only unary ops allowed here")
        elif token_value == "(":
            self.compile_expression()
        else:
            self.error("Invalid term syntax")

    def compile_string(self):
        string = self._tokenizer.return_token_value()
        length = len(string)
        self._vm_writer.write_push(VMWriter.CONST_SEGMENT, length)
        self._vm_writer.write_call("String.new", 1)  # returns a new string pointer at SP

        for i in range(length):
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, ord(string[i]))
            self._vm_writer.write_function("String.appendChar", 1)  # append characters one by one to String at SP

    def compile_integer(self):
        integer = self._tokenizer.return_token_value()
        self._vm_writer.write_push(VMWriter.CONST_SEGMENT, integer)

    def compile_keyword(self):
        keyword = self._tokenizer.return_token_value()

        if keyword == "true":
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, 0)
            self._vm_writer.write_arithmetic("neg")
        elif keyword == "this":
            self._vm_writer.write_push(VMWriter.POINTER_SEGMENT, 0)
        else:  # false and null
            self._vm_writer.write_push(VMWriter.CONST_SEGMENT, 0)

    def compile_var_name(self, name=None):
        if not name:
            if self._tokenizer.next():
                name = self._tokenizer.return_token_value()
            else:
                self.error("variable not declared properly")

        index, kind = self._symbol_table.index_of(name), self._symbol_table.kind_of(name)
        if kind:  # index can be 0, so checking kind if symbol exists
            if kind == "field":
                self._vm_writer.write_push(VMWriter.THIS_SEGMENT, index)
            else:
                self._vm_writer.write_push(kind, index)
        else:
            self.error("access to undefined variable")

        # evaluate array access
        if self._tokenizer.return_token_value() == "[":  # tokenizer has already advanced
            self.compile_expression()  # evaluated expression value at SP
            self._vm_writer.write_arithmetic("add")
            self._vm_writer.write_pop(VMWriter.POINTER_SEGMENT, 1)  # push array + base to THAT
            self._vm_writer.write_push(VMWriter.THAT_SEGMENT, 0)  # access [array + base] through THAT
        else:  # if variable access push variable value on stack
            self._tokenizer.go_back()

    def error(self, message):
        raise ValueError("Incorrect syntax/semantics. {} at line number {}".format(message, self._tokenizer.line_number))


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
