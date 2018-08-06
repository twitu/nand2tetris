import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class CodeWriter {
    private StringBuilder assemblyCommand;
    private String fileName; // default initial value
    private int comparisonCount;
    private static String functionName = "Sys.init";
    private static int functionCallCount = 0;

    private static final boolean DEBUG = false;

    public static final String closingCommand = "" +
            // end asm programme with loop
            "(END)\n@END\n0;JMP\n" +
            // the boolean operations assign true else jump to false subroutine
            // using register R13 to store return address to main routine
            "(EQUAL)\n@SP\nA=M-1\nD=M\n@FALSE\nD;JNE\n@SP\nA=M-1\nM=-1\n@R13\nA=M\n0;JMP\n" +
            "(GREATER)\n@SP\nA=M-1\nD=M\n@FALSE\nD;JLE\n@SP\nA=M-1\nM=-1\n@R13\nA=M\n0;JMP\n" +
            "(LESS)\n@SP\nA=M-1\nD=M\n@FALSE\nD;JGE\n@SP\nA=M-1\nM=-1\n@R13\nA=M\n0;JMP\n" +
            "(FALSE)\n@SP\nA=M-1\nM=0\n@R13\nA=M\n0;JMP\n";

    // optimized bootstrap code to set Sys.init stack frame and call Sys.init
    // Sys.init initializes registers as required to start executing programme
    // assumes LCL, ARG, THIS, THAT to be 0 and stores them accordingly
    public static final String bootStrapCode = "" +
            "@Sys.init$0\n" +
            "D=A\n" +
            "@256\n" + // store return address
            "M=D\n" +
            "@256\n" +
            "D=A\n" +
            "@ARG\n" + // write ARG
            "M=D\n" +
            "@257\n" + // store LCL
            "M=0\n" +
            "A=A+1\n" + // store ARG
            "M=0\n" +
            "A=A+1\n" + // store THIS
            "M=0\n" +
            "A=A+1\n" + // store THAT
            "M=0\n" +
            "D=A+1\n" +
            "@SP\n" + // write SP
            "M=D\n" +
            "@LCL\n" + // write LCL
            "M=D\n" +
            "@Sys.init\n" +
            "0;JMP\n" +
            "(Sys.init$0)\n";


    public CodeWriter(String filepath) {
        // initializing stack pointer not required as initialization done in test code
        // filename without .vm extension
        fileName = filepath.substring(0, filepath.lastIndexOf("."));
        comparisonCount = 0;
    }

    public void writeLabel(String arg1) throws java.lang.Exception{
        if (functionName == null) throw new Exception("Illegal syntax: Labels can only be defined inside functions.");
        assemblyCommand = new StringBuilder();
        // labels as filename.function$label
        assemblyCommand.append("(")
                .append(functionName).append(":").append(arg1).append(")\n");
    }

    public void writeGoto(String arg1) throws java.lang.Exception{
        if (functionName == null) throw new Exception("Illegal syntax: Labeled goto can only be defined inside functions.");
        assemblyCommand = new StringBuilder();
        assemblyCommand.append("@")
                .append(functionName).append(":").append(arg1).append("\n");
        assemblyCommand.append("0;JMP\n");
    }

    public void writeIf(String arg1) throws java.lang.Exception {
        if (functionName == null) throw new Exception("Illegal syntax: Labeled if-goto can only be used inside functions.");
        assemblyCommand = new StringBuilder();
        // POP operation
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("AM=M-1\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@")
                .append(functionName).append(":").append(arg1).append("\n");
        // Jump if true i.e. non zero value
        assemblyCommand.append("D;JNE\n");
    }

    public void writeArithmetic(String arg1) {
        assemblyCommand = new StringBuilder();
        if (arg1.equals("neg")) {
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("A=M-1\n");
            assemblyCommand.append("M=-M\n");
        } else if (arg1.equals("not")) {
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("A=M-1\n");
            assemblyCommand.append("M=!M\n");
        } else {
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("AM=M-1\n");
            assemblyCommand.append("D=M\n");
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("A=M-1\n"); // note tricky implementation to avoid incrementing value later
            if (arg1.equals("add")) assemblyCommand.append("M=M+D\n");
            else if (arg1.equals("and")) assemblyCommand.append("M=M&D\n");
            else if (arg1.equals("or")) assemblyCommand.append("M=M|D\n");
            else {
                assemblyCommand.append("M=M-D\n");
                if (!arg1.equals("sub")) {
                    assemblyCommand.append("@").append("RETURNHERE.").append(fileName).append("$").append(comparisonCount).append("\n");
                    assemblyCommand.append("D=A\n");
                    assemblyCommand.append("@R13\n");
                    assemblyCommand.append("M=D\n");
                    if (arg1.equals("eq")) assemblyCommand.append("@EQUAL\n0;JMP\n");
                    if (arg1.equals("gt")) assemblyCommand.append("@GREATER\n0;JMP\n");
                    if (arg1.equals("lt")) assemblyCommand.append("@LESS\n0;JMP\n");
                    assemblyCommand.append("(RETURNHERE.").append(fileName).append("$").append(comparisonCount++).append(")").append("\n");
                }
            }
            // incrementing stack pointer not required as it is already ahead of stored value
        }
    }

    public void writePushPop(int commandType, String arg1, int arg2) {
        assemblyCommand = new StringBuilder();
        if (commandType == Parser.C_POP) {
            switch (arg1) {
                case "pointer":
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("AM=M-1\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@").append(3 + arg2).append("\n");
                    assemblyCommand.append("M=D\n");
                    break;
                case "temp":
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("AM=M-1\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@").append(5 + arg2).append("\n");
                    assemblyCommand.append("M=D\n");
                    break;
                case "static":
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("AM=M-1\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@").append(fileName).append("$").append(arg2).append("\n");
                    assemblyCommand.append("M=D\n");
                    break;
                default:
                    // cases include ARG, LCL, THIS, THAT
                    assemblyCommand.append("@").append(arg1).append("\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@").append(arg2).append("\n");
                    assemblyCommand.append("D=D+A\n");
                    assemblyCommand.append("@R13\n"); // calculate and store address in RAM[13]
                    assemblyCommand.append("M=D\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("AM=M-1\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@R13\n");
                    assemblyCommand.append("A=M\n");
                    assemblyCommand.append("M=D\n");
            }
        } else {
            switch (arg1) {
                case "pointer":
                    assemblyCommand.append("@").append(3 + arg2).append("\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("A=M\n");
                    assemblyCommand.append("M=D\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("M=M+1\n");
                    break;
                case "temp":
                    assemblyCommand.append("@").append(5 + arg2).append("\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("A=M\n");
                    assemblyCommand.append("M=D\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("M=M+1\n");
                    break;
                case "static":
                    assemblyCommand.append("@").append(fileName).append("$").append(arg2).append("\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("A=M\n");
                    assemblyCommand.append("M=D\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("M=M+1\n");
                    break;
                case "constant":
                    assemblyCommand.append("@").append(arg2).append("\n");
                    assemblyCommand.append("D=A\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("A=M\n");
                    assemblyCommand.append("M=D\n");
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("M=M+1\n");
                    break;
                default:
                    // cases include ARG, LCL, THIS, THAT
                    assemblyCommand.append("@").append(arg1).append("\n");
                    assemblyCommand.append("D=M\n");
                    assemblyCommand.append("@").append(arg2).append("\n");
                    assemblyCommand.append("A=D+A\n");
                    assemblyCommand.append("D=M\n"); // store value of RAM[base+offset] in D
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("A=M\n");
                    assemblyCommand.append("M=D\n"); // write value from D into stack
                    assemblyCommand.append("@SP\n");
                    assemblyCommand.append("M=M+1\n");
            }
        }
    }

    public void writeFunctionCall(String arg1, int arg2) {
        // passing name of function and number of arguments
        assemblyCommand = new StringBuilder();
        // save return address label with filename function and number of calls
        assemblyCommand.append("@").append(arg1).append("$").append(functionCallCount).append("\n");
        assemblyCommand.append("D=A\n");
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("A=M\n");
        assemblyCommand.append("M=D\n");
        // save LCL
        assemblyCommand.append("@LCL\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("AM=M+1\n");
        assemblyCommand.append("M=D\n");
        // save ARG
        assemblyCommand.append("@ARG\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("AM=M+1\n");
        assemblyCommand.append("M=D\n");
        // save THIS
        assemblyCommand.append("@THIS\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("AM=M+1\n");
        assemblyCommand.append("M=D\n");
        // save THAT
        assemblyCommand.append("@THAT\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("AM=M+1\n");
        assemblyCommand.append("M=D\n");
        // write ARG and LCL
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("AM=M+1\n");
        assemblyCommand.append("D=A\n");
        // write LCL
        assemblyCommand.append("@LCL\n");
        assemblyCommand.append("M=D\n");
        // write ARG
        assemblyCommand.append("@").append(5 + arg2).append("\n"); // n args + 5 prev func stack
        assemblyCommand.append("D=D-A\n");
        assemblyCommand.append("@ARG\n");
        assemblyCommand.append("M=D\n");
        // goto function
        assemblyCommand.append("@").append(arg1).append("\n");
        assemblyCommand.append("0;JMP\n");
        // return label
        assemblyCommand.append("(").append(arg1).append("$").append(functionCallCount++).append(")\n");
    }

    public void writeFunction(String arg1, int arg2) {
        // function name is of format filename.function
        functionName = arg1;
        assemblyCommand = new StringBuilder();
        // write function label
        assemblyCommand.append("(").append(arg1).append(")\n");
        // check for 0 arguments to eliminate unnecessary instructions
        if (arg2 == 0) return;
        // initializing local variable to zero
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("A=M\n");
        for (int i = 0; i < arg2; i++) {
            assemblyCommand.append("M=0\n");
            assemblyCommand.append("A=A+1\n");
        }
        // setting SP to working stack
        assemblyCommand.append("D=A\n");
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("M=D\n");
    }

    public void writeFunctionReturn() {
        assemblyCommand = new StringBuilder();
        // store return address in RAM[13] or general[0]
        assemblyCommand.append("@5\n");
        assemblyCommand.append("D=A\n");
        assemblyCommand.append("@LCL\n");
        assemblyCommand.append("A=M\n");
        assemblyCommand.append("A=A-D\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@R13\n");
        assemblyCommand.append("M=D\n");
        // pop return value and store ARG[0] as top value of stack for callee
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("A=M-1\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@ARG\n");
        assemblyCommand.append("A=M\n");
        assemblyCommand.append("M=D\n");
        assemblyCommand.append("D=A+1\n");
        // reset SP to point to ARG[1] i.e. at blank location for callee
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("M=D\n");
        // read saved state of callee
        // saved THAT
        assemblyCommand.append("@LCL\n");
        assemblyCommand.append("AM=M-1\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@THAT\n");
        assemblyCommand.append("M=D\n");
        // saved THIS
        assemblyCommand.append("@LCL\n");
        assemblyCommand.append("AM=M-1\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@THIS\n");
        assemblyCommand.append("M=D\n");
        // saved ARG
        assemblyCommand.append("@LCL\n");
        assemblyCommand.append("AM=M-1\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@ARG\n");
        assemblyCommand.append("M=D\n");
        // load saved LCL value
        assemblyCommand.append("@LCL\n");
        assemblyCommand.append("A=M-1\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@LCL\n");
        assemblyCommand.append("M=D\n");
        // return address in RAM[13] return control to callee
        assemblyCommand.append("@R13\n");
        assemblyCommand.append("A=M\n");
        assemblyCommand.append("0;JMP\n");
    }

    public void getNextAssemblyCommand(Parser parser) throws java.lang.Exception{
        switch (parser.commandType()) {
            case Parser.C_POP:
                this.writePushPop(parser.commandType(), parser.arg1(), parser.arg2());
                break;
            case Parser.C_PUSH:
                this.writePushPop(parser.commandType(), parser.arg1(), parser.arg2());
                break;
            case Parser.C_ARITHMETIC:
                this.writeArithmetic(parser.arg1());
                break;
            case Parser.C_LABEL:
                this.writeLabel(parser.arg1());
                break;
            case Parser.C_GOTO:
                this.writeGoto(parser.arg1());
                break;
            case Parser.C_IF:
                this.writeIf(parser.arg1());
                break;
            case Parser.C_CALL:
                this.writeFunctionCall(parser.arg1(), parser.arg2());
                break;
            case Parser.C_FUNCTION:
                this.writeFunction(parser.arg1(), parser.arg2());
                break;
            case Parser.C_RETURN:
                this.writeFunctionReturn();
                break;
            default:
                throw new IllegalArgumentException("Invalid Input");
        }
        if (DEBUG) System.out.println(assemblyCommand.toString());
    }

    public static void main(String args[]) throws java.lang.Exception {
        File input = new File(args[0]);
        FileWriter fout;
        CodeWriter codeWriter;
        Parser parser;
        if (!input.exists()) throw new IOException("The given path does not exist");

        if (input.isDirectory()) {
            fout = new FileWriter(input.getCanonicalPath() + File.separatorChar + input.getName() + ".asm");

            // only accept .vm files using FileFilter
            File[] files = input.listFiles(pathname -> {
                if (pathname.getName().endsWith(".vm")) {
                    return true;
                } else {
                    return false;
                }
            });

            fout.write(bootStrapCode);

            for (File vmfile : files) {
                codeWriter = new CodeWriter(vmfile.getName());
                parser = new Parser(vmfile);
                while (parser.advance()) {
                    codeWriter.getNextAssemblyCommand(parser);
                    fout.write(codeWriter.assemblyCommand.toString());
                }
            }
        } else {
            if (!input.getName().endsWith(".vm")) {
                throw new IllegalArgumentException("Incorrect filename");
            } else {
                codeWriter = new CodeWriter(input.getName());
                parser = new Parser(input);
                fout = new FileWriter(input.getCanonicalPath().replace(".vm", ".asm"));
                while (parser.advance()) {
                    codeWriter.getNextAssemblyCommand(parser);
                    fout.write(codeWriter.assemblyCommand.toString());
                }

            }
        }
        fout.write(closingCommand);
        fout.close();
    }
}
