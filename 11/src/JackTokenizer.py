import os


class JackTokenizer:
    __slots__ = '_filepath', '_token', '_filecontent', '_cursor', '_return_token',\
                '_prev_token', '_prev_cursor', 'line_number'

    KEYWORD_TOKEN = 0
    SYMBOL_TOKEN = 1
    IDENTIFIER_TOKEN = 2
    INT_CONST_TOKEN = 3
    STRING_CONST_TOKEN = 4

    keywords = {"class", "constructor", "function", "method", "field",
                "static", "var", "int", "char", "boolean", "void", "true",
                "true", "false", "null", "this", "let", "do", "if", "else",
                "while", "return"}
    symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
               '/', '&', ',', '<', '>', '=', '~', '|'}
    whitespace = {'\n', '\t', '', ' '}
    token_literal_name = ["keyword", "symbol", "identifier", "integerConstant", "stringConstant"]
    special_xml = {'<': "&lt;", '>': "&gt;", '\"': "&quot;", '&': "&amp;"}

    def __init__(self, filepath):
        self._filepath = filepath
        self._token = None
        self._prev_token = None
        self._cursor = 0
        self._prev_cursor = 0
        self.line_number = 0
        self._return_token = [
            self.keyword,
            self.symbol,
            self.identifier,
            self.int_val,
            self.string_val,
        ]
        try:
            with open(self._filepath, 'r') as inputstream:
                self._filecontent = inputstream.read()
        except IOError:
            print("Please check given file path.")

    def advance(self):
        # advances file cursor and tokenizes the next possible token
        # also identifies and stores token type
        # returns self._token to be used as a boolean value check
        while self._cursor < len(self._filecontent):
            character = self._filecontent[self._cursor]
            words = []
            self._prev_cursor = self._cursor

            if character == '/':  # ignore comments
                self._cursor += 1
                next_character = self._filecontent[self._cursor]
                if next_character == '*':
                    self._cursor += 1
                    while not (self._filecontent[self._cursor] == '*' and self._filecontent[self._cursor + 1] == '/'):
                        self._cursor += 1
                        if self._filecontent[self._cursor] == '\n':
                            self.line_number += 1
                    self._cursor += 1
                elif next_character == '/':  # the other possible character is /
                    self._cursor += 1
                    self.line_number += 1
                    while self._filecontent[self._cursor] != '\n':
                        self._cursor += 1
                else:  # special case because '/' is also a symbol
                    self._prev_token = self._token
                    self._token = character
                    return self._token
            elif character == '\"':  # check for " to tokenize strings without the double quotes
                words.append('\"')
                while self._cursor < len(self._filecontent):
                    self._cursor += 1
                    letters = self._filecontent[self._cursor]
                    if letters != '\"':
                        words.append(letters)
                    else:
                        words.append('\"')
                        self._cursor += 1
                        self._prev_token = self._token
                        self._token = ''.join(words)
                        return self._token
            elif character in JackTokenizer.symbols:  # check if character is a symbol tokenize it
                self._cursor += 1
                self._prev_token = self._token
                self._token = character
                return self._token
            elif character in JackTokenizer.whitespace:  # ignore white space
                if character == '\n':
                    self.line_number += 1
            else:  # tokenize keyword integer or identifier
                words = [character]
                while self._cursor < len(self._filecontent):
                    self._cursor += 1
                    letters = self._filecontent[self._cursor]
                    if letters not in JackTokenizer.whitespace and letters not in JackTokenizer.symbols:
                        words.append(letters)
                    else:
                        # do not increment cursor since it is already pointing to next letter after token
                        self._prev_token = self._token
                        self._token = ''.join(words)
                        return self._token

            self._cursor += 1

        # return None when iterated over file contents
        self._token = None
        return self._token

    def go_back(self):
        # should not be called twice consecutively
        self._token = self._prev_token
        self._cursor = self._prev_cursor

    def token_type(self):
        # return type of token
        if self._token in JackTokenizer.keywords:
            return JackTokenizer.KEYWORD_TOKEN
        elif self._token in JackTokenizer.symbols:
            return JackTokenizer.SYMBOL_TOKEN
        elif self._token[0].isnumeric():
            return JackTokenizer.INT_CONST_TOKEN
        elif self._token[0] == '\"':
            return JackTokenizer.STRING_CONST_TOKEN
        else:
            return JackTokenizer.IDENTIFIER_TOKEN

    def return_token_value(self, token_type=None):
        if token_type:
            return self._return_token[token_type]()
        else:
            return self._return_token[self.token_type()]()

    def keyword(self):
        # should only be called when token is of type KEYWORD
        return self._token

    def symbol(self):
        # should only be called when token is of type SYMBOL
        # check and handle special xml tokens
        if self._token in JackTokenizer.special_xml.keys():
            return JackTokenizer.special_xml[self._token]
        return self._token

    def identifier(self):
        # should only be called when token is of type IDENTIFIER
        return self._token

    def int_val(self):
        # should only be called when token is of type INT_CONST
        return int(self._token)

    def string_val(self):
        # should only be called when token is of type STRING_CONST
        # ignoring explicit quotes
        return self._token[1:-1]


# function for testing purposes
# input: filename.jack
# output: filenameTokenized.xml
def tokenize(inputpath):
    tokenizer = JackTokenizer(inputpath)
    outputfile = inputpath.replace(".jack", "Tokenized.xml")
    tokenized_xml = ["<tokens>"]

    while tokenizer.advance():
        type_of_token = JackTokenizer.token_literal_name[tokenizer.token_type()]
        token = tokenizer.return_token_value()

        tokenized_xml.append("<{}> {} </{}>".format(type_of_token, token, type_of_token))

    tokenized_xml.append("</tokens>\n")
    with open(outputfile, 'w') as outputstream:
        outputstream.write('\n'.join(tokenized_xml))


if __name__ == '__main__':
    inputpath = "../Square"
    if os.path.isfile(inputpath):
        tokenize(inputpath)
    elif os.path.isdir(inputpath):
        for file in os.listdir(inputpath):
            if file.endswith(".jack"):
                tokenize(os.path.join(inputpath, file))
