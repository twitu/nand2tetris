import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class Parser {
    private Scanner in;
    private String command;
    private String[] split;

    public static final int C_ARITHMETIC = 0;
    public static final int C_PUSH = 1;
    public static final int C_POP = 2;
    public static final int C_LABEL = 3;
    public static final int C_GOTO = 4;
    public static final int C_IF = 5;
    public static final int C_FUNCTION = 6;
    public static final int C_RETURN = 7;
    public static final int C_CALL = 8;

    public Parser(String filename) throws FileNotFoundException{
        in = new Scanner(new FileInputStream(filename));
    }

    public boolean advance() {
        while (in.hasNextLine()) {
            command = in.nextLine();
            if (!command.equals("") && command.charAt(0)!='/') {
                if (command.indexOf('/')!=-1) {
                    command = command.substring(0, command.indexOf('/'));
                }
                command = command.trim();
                split = command.split(" ");
                return true;
            }
        }
        in.close();
        return false;
    }

    public int commandType() {
        if (split[0].equals("pop")) return C_POP;
        else if (split[0].equals("push")) return C_PUSH;
        else {
            return C_ARITHMETIC;
        }
    }

    public String arg1() {
        if (split.length==1) return split[0];
        else return split[1];
    }

    public Integer arg2() {
        if (split.length>2) return Integer.parseInt(split[2]);
        else return null;
    }
}
