import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.HashMap;
import java.util.Scanner;

public class Parser {
    private Scanner in;
    private String[] split;
    private static final HashMap<String, String> memorymapping = new HashMap<>();

    // maps vm memory calls to registers implemented in memory
    // pointer, temp, static are virtual hence are implemented in CodeWriter
    static {
        memorymapping.put("argument", "ARG");
        memorymapping.put("local" , "LCL");
        memorymapping.put("this", "THIS");
        memorymapping.put("that", "THAT");
    }

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
            String command = in.nextLine();
            if (!command.equals("") && command.charAt(0)!='/') {
                if (command.indexOf('/')!=-1) {
                    command = command.substring(0, command.indexOf('/'));
                }

                // remove any extra spaces and split into parts
                command = command.trim();
                split = command.split(" ");
                for (int i=0; i<split.length; i++) {
                    split[i] = split[i].trim();
                }

                // map to predefined virtual register if possible
                if (split.length > 1 && memorymapping.containsKey(split[1])) {
                    split[1] = memorymapping.get(split[1]);
                }
                return true;
            }
        }
        in.close();
        return false;
    }

    public int commandType() {
        switch (split[0]) {
            case ("pop"): return C_POP;
            case ("push"): return C_PUSH;
            case ("label"): return C_LABEL;
            case ("goto"): return C_GOTO;
            case ("if-goto"): return C_IF;
            case ("function"): return C_FUNCTION;
            case ("call"): return C_CALL;
            case ("return"): return C_RETURN;
            default: return C_ARITHMETIC;
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
