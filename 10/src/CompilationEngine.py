class CompilationEngine:
    __slots__ = '_tokenizer', '_output_stream', '_xml_output', '_indentation', \
                '_keyword_compile_function_dict', '_statement_compile_function_dict'

    string_format_terminal = "<{}> {} </{}>"

    def __init__(self, tokenizer, outputstream):
        self._tokenizer = tokenizer
        self._output_stream = outputstream
        self._xml_output = []
        self._indentation = 0
        self._keyword_compile_function_dict = {
            "class": self.compile_class,
            "static": self.compile_var_dec,
            "final": self.compile_var_dec,
            "constructor": self.compile_subroutine,
            "method": self.compile_subroutine,
            "function": self.compile_subroutine,
            "var": self.compile_var_dec,
            "let": self.compile_let,
            "if": self.compile_if,
            "while": self.compile_while,
            "do": self.compile_do,
            "return": self.compile_return,
        }

        self._statement_compile_function_dict = {
            "let": self.compile_let,
            "do": self.compile_do,
            "while": self.compile_while,
            "if": self.compile_if,
            "return": self.compile_return,
        }
        self.compile_class()

    def advance_and_print(self, terminate):
        # advances and prints terminals until it encounters termination character
        while self._tokenizer.advance():
            token_type = self._tokenizer.token_literal_name[self._tokenizer.token_type()]
            token = self._tokenizer.return_token_value()
            self._xml_output.append(' ' * self._indentation +
                                    CompilationEngine.string_format_terminal.format(
                                        token_type,
                                        token,
                                        token_type)
                                    )
            if token == terminate:  # appends termination character string to xml output
                return

    def compile_class(self):
        self._xml_output.append("<class>")
        self._indentation += 2
        self.class_compile_var_dec()
        self.compile_subroutine()
        self._indentation -= 2
        self._xml_output.append("</class>")

    def class_compile_var_dec(self):
        self._xml_output.append(' ' * self._indentation + "<classVarDec>")
        self._indentation += 2
        self.advance_and_print(';')
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</classVarDec>")

    def compile_subroutine(self):
        self._xml_output.append(' ' * self._indentation + "<subroutineDec>")
        self._indentation += 2
        self.advance_and_print('(')
        self.compile_parameter_list()
        self._tokenizer.go_back() # fix faulty printing of closing bracket
        self.advance_and_print(')')
        self._xml_output.append(' ' * self._indentation + "<subroutineBody>")
        self._indentation += 2
        self.advance_and_print('{')
        while self._tokenizer.advance() and self._tokenizer.return_token_value == "var":
            self._tokenizer.go_back()
            self.compile_var_dec()
        else:
            self._xml_output.append(' ' * self._indentation + "<statements>")
            self.compile_statements()
            self._xml_output.append(' ' * self._indentation + "</statements>")
        self._xml_output.append(' ' * self._indentation + "</subroutineBody>")
        self._xml_output.append("</subroutineDec>")

    def compile_parameter_list(self):
        # note subroutineDec ends with subRoutineBody
        self._xml_output.append(' ' * self._indentation + "<parameterList>")
        self._indentation += 2
        self.advance_and_print(')')
        self._indentation -= 2
        self._xml_output.pop() # remove faulty indentation and position of closing bracket
        self._xml_output.append(' ' * self._indentation + "</parameterList>")

    def compile_var_dec(self):
        self._xml_output.append(' ' * self._indentation + "<varDec>")
        self._indentation += 2
        self.advance_and_print(';')
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</varDec>")

    def compile_statements(self):
        while self._tokenizer.advance():
            # choose next statement to compile based on keyword
            # let, if, while, do, return
            next_function = self._statement_compile_function_dict[self._tokenizer.return_token_value()]
            self._tokenizer.go_back()
            next_function()


    def compile_do(self):
        self._xml_output.append(' ' * self._indentation + "<doStatement>")
        self._indentation += 2
        self.advance_and_print()
        self._token_stack.append("</doStatement>")

    def compile_let(self):
        self._xml_output.append("<letStatement>")
        self._indentation.append(" ")
        self._indentation.append(" ")
        self._completion_symbol_stack.append(';')
        self._token_stack.append("</letStatement>")

    def compile_while(self):
        self._xml_output.append("<whileStatement>")
        self._indentation.append(" ")
        self._indentation.append(" ")
        self._completion_symbol_stack.append(';')
        self._token_stack.append("</whileStatement>")

    def compile_return(self):
        self._xml_output.append("<returnStatement>")
        self._indentation.append(" ")
        self._indentation.append(" ")
        self._completion_symbol_stack.append(';')
        self._token_stack.append("</returnStatement>")

    def compile_if(self):
        self._xml_output.append("<ifStatement>")
        self._indentation.append(" ")
        self._indentation.append(" ")
        self._completion_symbol_stack.append('}')
        self._token_stack.append("</ifStatement>")

    def compile_expression(self):
        self._xml_output.append("<expression>")
        self._indentation.append(" ")
        self._indentation.append(" ")
        self._completion_symbol_stack.append(')')
        self._token_stack.append("</expression>")

    def compile_term(self):

    def compile_expression_list(self):
