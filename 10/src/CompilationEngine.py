import sys
import os

from JackTokenizer import JackTokenizer


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

    def advance_and_print(self, terminate=(), count=-1):
        # advances and prints terminals until it encounters termination character
        # also can specify number of tokens to print
        # by default it will keep tokenizing until terminating character
        while count != 0 and self._tokenizer.advance():
            token_type = self._tokenizer.token_literal_name[self._tokenizer.token_type()]
            token = self._tokenizer.return_token_value()
            self._xml_output.append(' ' * self._indentation +
                                    CompilationEngine.string_format_terminal.format(
                                        token_type,
                                        token,
                                        token_type)
                                    )
            count -= 1
            # appends termination character string to xml output
            if token in terminate:  # finishes on finding termination token
                return

    def compile_class(self):
        self._xml_output.append("<class>")
        self._indentation += 2
        self.advance_and_print(['{'])
        while self._tokenizer.advance() and self._tokenizer.return_token_value() in ["static", "field"]:
            self._tokenizer.go_back()
            self.class_compile_var_dec()
        else:
            self._tokenizer.go_back()

        while self._tokenizer.advance() and self._tokenizer.return_token_value() in \
                ["constructor", "function", "method"]:
            self._tokenizer.go_back()
            self.compile_subroutine()
        else:
            self._tokenizer.go_back()

        self.advance_and_print(['}'])
        self._indentation -= 2
        self._xml_output.append("</class>")

    def class_compile_var_dec(self):
        self._xml_output.append(' ' * self._indentation + "<classVarDec>")
        self._indentation += 2
        self.advance_and_print([';'])
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</classVarDec>")

    def compile_subroutine(self):
        self._xml_output.append(' ' * self._indentation + "<subroutineDec>")
        self._indentation += 2
        self.advance_and_print(['('])
        self.compile_parameter_list()
        self._tokenizer.go_back()  # fix faulty printing of closing bracket
        self.advance_and_print([')'])
        self._xml_output.append(' ' * self._indentation + "<subroutineBody>")
        self._indentation += 2
        self.advance_and_print(['{'])
        while self._tokenizer.advance() and self._tokenizer.return_token_value() == "var":
            self._tokenizer.go_back()
            self.compile_var_dec()
        else:
            self._tokenizer.go_back()
            self.compile_statements()
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</subroutineBody>")
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</subroutineDec>")

    def compile_parameter_list(self):
        # note subroutineDec ends with subRoutineBody
        self._xml_output.append(' ' * self._indentation + "<parameterList>")
        self._indentation += 2
        self.advance_and_print([')'])
        self._indentation -= 2
        self._xml_output.pop() # remove faulty indentation and position of closing bracket
        self._xml_output.append(' ' * self._indentation + "</parameterList>")

    def compile_var_dec(self):
        self._xml_output.append(' ' * self._indentation + "<varDec>")
        self._indentation += 2
        self.advance_and_print([';'])
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</varDec>")

    def compile_statements(self):
        self._xml_output.append(' ' * self._indentation + "<statements>")
        self._indentation += 2
        while self._tokenizer.advance() and self._tokenizer.return_token_value() != '}':
            # choose next statement to compile based on keyword
            # let, if, while, do, return
            next_function = self._statement_compile_function_dict[self._tokenizer.return_token_value()]
            self._tokenizer.go_back()
            next_function()
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</statements>")
        self._tokenizer.go_back()
        self.advance_and_print(['}'])

    def compile_do(self):
        self._xml_output.append(' ' * self._indentation + "<doStatement>")
        self._indentation += 2
        # pushed subroutine name or instance method
        self.advance_and_print(['('])
        self.compile_expression_list()  # pushes closing bracket
        self.advance_and_print([';'])
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</doStatement>")

    def compile_let(self):
        self._xml_output.append(' ' * self._indentation + "<letStatement>")
        self._indentation += 2
        self.advance_and_print(['[', '='])
        if self._tokenizer.return_token_value() == '[':  # check for optional expression
            self.compile_expression()  # expression will end with ']'
            self.advance_and_print(['='])
        self.compile_expression()  # expression will end with ';'
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</letStatement>")

    def compile_while(self):
        self._xml_output.append(' ' * self._indentation + "<whileStatement>")
        self._indentation += 2
        self.advance_and_print(['('])
        self.compile_expression()
        self.advance_and_print(['{'])
        self.compile_statements()
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</whileStatement>")

    def compile_return(self):
        self._xml_output.append(' ' * self._indentation + "<returnStatement>")
        self._indentation += 2
        self.advance_and_print(["return"])
        if self._tokenizer.advance() and self._tokenizer.return_token_value() != ';':
            self._tokenizer.go_back()
            self.compile_expression()
        else:
            self._tokenizer.go_back()
            self.advance_and_print([';'])
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</returnStatement>")

    def compile_if(self):
        self._xml_output.append(' ' * self._indentation + "<ifStatement>")
        self._indentation += 2
        self.advance_and_print(['('])
        self.compile_expression()
        self.advance_and_print(['{'])
        self.compile_statements()
        if self._tokenizer.advance() and self._tokenizer.return_token_value() == "else":
            self._tokenizer.go_back()
            self.advance_and_print(['{'])
            self.compile_statements()
        else:
            self._tokenizer.go_back()
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</ifStatement>")

    def compile_expression(self):
        self._xml_output.append(' ' * self._indentation + "<expression>")
        self._indentation += 2
        self.compile_term()
        while self._tokenizer.advance() and self._tokenizer.return_token_value() not in [')', ']', ',', ';']:
            # check and push of to xml op
            self._tokenizer.go_back()
            self.advance_and_print((), 1)  # push the op to output
            # push term to xml
            self.compile_term()
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</expression>")
        # push detected ending character or closing brace
        self._tokenizer.go_back()
        self.advance_and_print((), 1)

    def compile_term(self):
        self._xml_output.append(' ' * self._indentation + "<term>")
        self._indentation += 2
        self.advance_and_print((), 1)
        if self._tokenizer.return_token_value() == '(':  # evaluate expression
            self.compile_expression()
        elif self._tokenizer.return_token_value() in ['-', '~']:  # handle unary op
            self.compile_term()
        else:
            self.advance_and_print((), 1)
            if self._tokenizer.return_token_value() == '(':
                self.compile_expression_list()
            elif self._tokenizer.return_token_value() == '[':
                self.compile_expression()
            elif self._tokenizer.return_token_value() == '.':  # method call
                self.advance_and_print((), 2)
                if self._tokenizer.return_token_value() == '(':
                    self.compile_expression_list()
                else:
                    # tokenizer should go back if it encounters expression terminating characters
                    self._tokenizer.go_back()
                    self._xml_output.pop()
            else:
                # tokenizer should go back if it encounters expression terminating characters
                self._tokenizer.go_back()
                self._xml_output.pop()
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</term>")

    def compile_expression_list(self):
        close = ""
        self._xml_output.append(' ' * self._indentation + "<expressionList>")
        self._indentation += 2
        while self._tokenizer.advance() and self._tokenizer.return_token_value() != ')':
            self._tokenizer.go_back()
            self.compile_expression()
            if self._tokenizer.return_token_value() == ')':
                break
        else:
            self._tokenizer.go_back()
            self.advance_and_print([')'])
        close = self._xml_output.pop()[2:]
        self._indentation -= 2
        self._xml_output.append(' ' * self._indentation + "</expressionList>")
        if close:
            self._xml_output.append(close)

    def write_to_file(self):
        with open(self._output_stream, 'w') as output:
            output.write('\n'.join(self._xml_output))
            output.write('\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError("Please give a file/directory path as argument")

    input_path = sys.argv[1]
    if os.path.isfile(input_path) and input_path.endswith(".jack"):
        tokenizer = JackTokenizer(input_path)
        compiler = CompilationEngine(tokenizer, input_path.replace(".jack", "Compiled.xml"))
        compiler.write_to_file()
    elif os.path.isdir(input_path):
        for file in os.listdir(input_path):
            if file.endswith(".jack"):
                tokenizer = JackTokenizer(os.path.join(input_path, file))
                compiler = CompilationEngine(tokenizer,
                                             os.path.join(input_path,file.replace(".jack", "Compiled.xml")),
                                             )
                compiler.write_to_file()
    else:
        raise ValueError("incorrect path given")
