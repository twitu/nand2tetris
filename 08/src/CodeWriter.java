import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class CodeWriter {
    private FileWriter fout;
    private StringBuilder assemblyCommand;
    private String fileName;
    private int count;
    private int staticCount;
    private static final boolean DEBUG = false;

    public CodeWriter(String filename) throws IOException{
        fileName = filename.substring(filename.lastIndexOf("/")+1, filename.lastIndexOf("."));
        fout = new FileWriter(new File(filename.substring(0, filename.indexOf(".vm")) + ".asm"));
        count = 0;
        staticCount = 0;
        // initializing stack pointer not required as initialization done in test code
    }

    public void close() throws IOException{
        assemblyCommand = new StringBuilder();
        // end asm programme with loop
        assemblyCommand.append("(END)\n@END\n0;JMP\n");
        // the boolean operations assign true else jump to false subroutine
        // using register R13 to store return address to main routine
        assemblyCommand.append("(EQUAL)\n@SP\nA=M\nD=M\n@FALSE\nD;JNE\n@SP\nA=M\nM=-1\n@R13\nA=M\n0;JMP\n");
        assemblyCommand.append("(GREATER)\n@SP\nA=M\nD=M\n@FALSE\nD;JLE\n@SP\nA=M\nM=-1\n@R13\nA=M\n0;JMP\n");
        assemblyCommand.append("(LESS)\n@SP\nA=M\nD=M\n@FALSE\nD;JGE\n@SP\nA=M\nM=-1\n@R13\nA=M\n0;JMP\n");
        assemblyCommand.append("(FALSE)\n@SP\nA=M\nM=0\n@R13\nA=M\n0;JMP\n");
        fout.write(assemblyCommand.toString());
        fout.close();
    }

    public void writeLabel(String arg1) throws IOException{
        assemblyCommand = new StringBuilder();
        assemblyCommand.append("(").append(arg1).append(")\n");
        fout.write(assemblyCommand.toString());
    }

    public void writeGoto(String arg1) throws IOException{
        assemblyCommand = new StringBuilder();
        assemblyCommand.append("@").append(arg1).append("\n");
        assemblyCommand.append("0;JMP\n");
        fout.write(assemblyCommand.toString());
    }

    public void writeIf(String arg1) throws IOException{
        assemblyCommand = new StringBuilder();
        // POP operation
        assemblyCommand.append("@SP\n");
        assemblyCommand.append("AM=M-1\n");
        assemblyCommand.append("D=M\n");
        assemblyCommand.append("@").append(arg1).append("\n");
        // Jump if true i.e. non zero value
        assemblyCommand.append("D;JNE\n");
        fout.write(assemblyCommand.toString());
    }

    public void writeArithmetic(String arg1) throws IOException{
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
            assemblyCommand.append("AM=M-1\n");
            if (arg1.equals("add")) assemblyCommand.append("M=M+D\n");
            else if (arg1.equals("and")) assemblyCommand.append("M=M&D\n");
            else if (arg1.equals("or")) assemblyCommand.append("M=M|D\n");
            else {
                assemblyCommand.append("M=M-D\n");
                if (!arg1.equals("sub")) {
                    assemblyCommand.append("@RETURNHERE").append(count).append("\n");
                    assemblyCommand.append("D=A\n");
                    assemblyCommand.append("@R13\n");
                    assemblyCommand.append("M=D\n");
                    if (arg1.equals("eq")) assemblyCommand.append("@EQUAL\n0;JMP\n");
                    if (arg1.equals("gt")) assemblyCommand.append("@GREATER\n0;JMP\n");
                    if (arg1.equals("lt")) assemblyCommand.append("@LESS\n0;JMP\n");
                    assemblyCommand.append("(RETURNHERE").append(count++).append(")").append("\n");
                }
            }
            // incrementing stack pointer after code for all possible operations are done
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("M=M+1\n");
        }
        fout.write(assemblyCommand.toString());
    }

    public void writePushPop(int commandType, String arg1, int arg2) throws IOException{
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
                    assemblyCommand.append("@").append(fileName).append(".").append(arg2).append("\n");
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
                    assemblyCommand.append("@").append(fileName).append(".").append(arg2).append("\n");
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
        fout.write(assemblyCommand.toString());
    }

    public static void main(String args[]) throws IOException{
        CodeWriter codeWriter = new CodeWriter(args[0]);
        Parser parser = new Parser(args[0]);
        while (parser.advance()) {
            if (parser.commandType()==Parser.C_POP || parser.commandType()==Parser.C_PUSH) {
                codeWriter.writePushPop(parser.commandType(), parser.arg1(), parser.arg2());
            } else if (parser.commandType()==Parser.C_ARITHMETIC){
                codeWriter.writeArithmetic(parser.arg1());
            } else if (parser.commandType()==Parser.C_LABEL) {
                codeWriter.writeLabel(parser.arg1());
            } else if (parser.commandType()==Parser.C_GOTO) {
                codeWriter.writeGoto(parser.arg1());
            } else if (parser.commandType()==Parser.C_IF) {
                codeWriter.writeIf(parser.arg1());
            } else {
                throw new IllegalArgumentException("Invalid Input");
            }
        }
        codeWriter.close();
    }
}
