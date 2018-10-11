class VMWriter:

    CONST_SEGMENT = "constant"
    POINTER_SEGMENT = "pointer"
    THAT_SEGMENT = "that"
    THIS_SEGMENT = "this"
    TEMP_SEGMENT = "temp"
    ARG_SEGMENT = "argument"
    LOCAL_SEGMENT = "local"

    def __init__(self, output_stream):
        self._output_stream = output_stream
        self._output_file = open(output_stream, 'w')
        self._arithmetic_symbol = {
            "+": "add",
            "-": "sub",
            "~": "neg",
            "<": "lt",
            ">": "gt",
            "=": "eq",
            "&": "and",
            "|": "or",
            "!": "not",
        }

    def write(self, vm_instruction):
        self._output_file.write(vm_instruction)

    def write_push(self, segment, index):
        if segment == "field":
            segment = "this"
        if segment == "var":
            segment = "local"
        vm = "push {} {}\n".format(segment, index)
        self.write(vm)

    def write_pop(self, segment, index):
        if segment == "field":
            segment = "this"
        if segment == "var":
            segment = "local"
        vm = "pop {} {}\n".format(segment, index)
        self.write(vm)

    def write_arithmetic(self, symbol):  # command is the vm instruction
        self.write(self._arithmetic_symbol[symbol] + '\n')

    def write_label(self, label):
        vm = "label L{}\n".format(label)
        self.write(vm)

    def write_goto(self, label):
        vm = "goto L{}\n".format(label)
        self.write(vm)

    def write_if(self, label):
        vm = "if-goto L{}\n".format(label)
        self.write(vm)

    def write_call(self, name, nargs):
        vm = "call {} {}\n".format(name, nargs)
        self.write(vm)

    def write_function(self, name, nlocals):
        vm = "function {} {}\n".format(name, nlocals)
        self.write(vm)

    def write_return(self):
        self.write("return\n")
