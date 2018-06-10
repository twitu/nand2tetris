import java.io.*;

public class Assembler {
    public static void main(String args[]) throws java.io.IOException{
        Parser firstParser = new Parser(args[0]);
        SymbolTable symbolTable = new SymbolTable();

        String symbol;
        int address, commandCount=-1;
        StringBuilder binary = new StringBuilder(16);
        FileWriter fout = new FileWriter(new File(args[0].substring(0, args[0].indexOf(".asm")) + "Assembled.hack"));
        while (firstParser.advance()) {
            commandCount++;
            if (firstParser.commandType()==2) {
                symbol = firstParser.symbol();
                symbolTable.addEntryLabel(symbol, commandCount);
                commandCount--;
            }
        }

        Parser secondParser = new Parser(args[0]);
        while (secondParser.advance()) {
            if (secondParser.commandType()==0) {
                symbol = secondParser.symbol();
                if (Character.isAlphabetic(symbol.charAt(0))) {
                    if (!symbolTable.contains(symbol)) {
                        address = symbolTable.addEntryVariable(symbol);
                    } else {
                        address = symbolTable.getAddress(symbol);
                    }
                } else {
                    address = Integer.parseInt(symbol);
                }
                fout.write(String.format("%16s\n", Integer.toBinaryString(address)).replace(" ", "0"));
            } else if (secondParser.commandType()==1) {
                binary.replace(0, 3, "111");
                binary.replace(3, 10, Code.comp(secondParser.comp()));
                binary.replace(10, 13, Code.dest(secondParser.dest()));
                binary.replace(13, 16, Code.jump(secondParser.jump()));
                fout.write(binary.toString());
                fout.write('\n');
            }
            fout.flush();
        }
        fout.close();
    }
}
