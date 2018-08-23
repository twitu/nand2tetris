class VMWriter:

    def __init__(self, output_stream):
        self._output_stream = output_stream
        self._output_file = open(output_stream, 'w')

    def write(self, vm_instruction):
        self._output_file.write(vm_instruction)

    def write_push(self, segment, index):
        vm = "push {} {}\n".format(segment, index)
        self.write(vm)

    def write_pop(self, segment, index):
        vm = "pop {} {}\n".format(segment, index)
        self.write(vm)

    def write_arithmetic(self, command):  # command is the vm instruction
        self.write(command + '\n')

    def write_label(self, label):
        vm = "label {}\n".format(label)
        self.write(vm)

    def write_goto(self, label):
        vm = "goto {}\n".format(label)
        self.write(vm)

    def write_if(self, label):
        vm = "if-goto {}".format(label)
        self.write(vm)

    def write_call(self, name, nargs):
        vm = "call {} {}\n".format(name, nargs)
        self.write(vm)

    def write_function(self, name, nlocals):
        vm = "function {} {}\n".format(name, nlocals)
        self.write(vm)
        for i in range(nlocals):
            self.write_push("local", i)

    def write_return(self):
        self.write("return;")
