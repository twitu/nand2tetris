import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class CodeWriter {
    private FileWriter fout;
    private StringBuilder assemblyCommand;
    private int count;

    public CodeWriter(String filename) throws IOException{
        fout = new FileWriter(new File(filename.substring(0, filename.indexOf(".vm")) + ".asm"));
        count = 0;
        // initializing stack pointer
        assemblyCommand = new StringBuilder("@256\nD=A\n@SP\nM=D\n");
        fout.write(assemblyCommand.toString());
    }

    public void close() throws IOException{
        assemblyCommand = new StringBuilder();
        // end asm programme with loop
        assemblyCommand.append("(END)\n@END\n0;JMP\n");
        // the boolean operations assign true to compliment else jump to false subroutine
        // using register R5 to store address of main routine
        assemblyCommand.append("(EQUAL)\n@FALSE\nD;JNE\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n@R5\nA=M\n0;JMP\n");
        assemblyCommand.append("(GREATER)\n@FALSE\nD;JLE\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n@R5\nA=M\n0;JMP\n");
        assemblyCommand.append("(LESS)\n@FALSE\nD;JGE\n@SP\nA=M\nM=-1\n@SP\nM=M+1\n@R5\nA=M\n0;JMP\n");
        assemblyCommand.append("(FALSE)\n@SP\nA=M\nM=0\n@SP\nM=M+1\n@R5\nA=M\n0;JMP\n");
        fout.write(assemblyCommand.toString());
        fout.close();
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
            if (arg1.equals("add")) assemblyCommand.append("D=M+D\n");
            else if (arg1.equals("and")) assemblyCommand.append("D=M&D\n");
            else if (arg1.equals("or")) assemblyCommand.append("D=M|D\n");
            else {
                assemblyCommand.append("D=M-D\n");
                if (!arg1.equals("sub")) {
                    assemblyCommand.append("@R6\n");
                    assemblyCommand.append("M=D\n");
                    assemblyCommand.append("@RETURNHERE").append(count).append("\n");
                    assemblyCommand.append("D=A\n");
                    assemblyCommand.append("@R5\n");
                    assemblyCommand.append("M=D\n");
                    assemblyCommand.append("@R6\n");
                    assemblyCommand.append("D=M\n");
                    if (arg1.equals("eq")) assemblyCommand.append("@EQUAL\n0;JMP\n");
                    if (arg1.equals("gt")) assemblyCommand.append("@GREATER\n0;JMP\n");
                    if (arg1.equals("lt")) assemblyCommand.append("@LESS\n0;JMP\n");
                    assemblyCommand.append("(RETURNHERE").append(count++).append(")").append("\n");
                    fout.write(assemblyCommand.toString());
                    return;
                }
            }
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("A=M\n");
            assemblyCommand.append("M=D\n");
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("M=M+1\n");
        }
        fout.write(assemblyCommand.toString());
    }

    public void writePushPop(int commandType, String arg1, int arg2) throws IOException{
        assemblyCommand = new StringBuilder();
        if (commandType == Parser.C_POP) {
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("AM=M-1\n");
            assemblyCommand.append("D=M\n");
            assemblyCommand.append("@").append(arg1).append("\n");
            assemblyCommand.append("A=A+").append(arg2).append("\n");
            assemblyCommand.append("M=D\n");
            fout.write(assemblyCommand.toString());
        } else {
            if (!arg1.equals("constant")) {
                assemblyCommand.append("@").append(arg1).append("\n");
                assemblyCommand.append("A=A+").append(arg2).append("\n");
                assemblyCommand.append("D=M\n");
            } else {
                assemblyCommand.append("@").append(arg2).append("\n");
                assemblyCommand.append("D=A\n");
            }
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("A=M\n");
            assemblyCommand.append("M=D\n");
            assemblyCommand.append("@SP\n");
            assemblyCommand.append("M=M+1\n");
            fout.write(assemblyCommand.toString());
        }
    }

    public static void main(String args[]) throws IOException{
        CodeWriter codeWriter = new CodeWriter(args[0]);
        Parser parser = new Parser(args[0]);
        while (parser.advance()) {
            if (parser.commandType()==Parser.C_POP || parser.commandType()==Parser.C_PUSH) {
                codeWriter.writePushPop(parser.commandType(), parser.arg1(), parser.arg2());
            } else {
                codeWriter.writeArithmetic(parser.arg1());
            }
        }
        codeWriter.close();
    }
}
