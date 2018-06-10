import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.util.Scanner;
import java.util.regex.Pattern;

public class Parser {
    private Scanner in;
    private String command;

    public Parser(String filename) throws FileNotFoundException{
        in = new Scanner(new FileInputStream(filename));
    }

    // Assuming the Hack code is syntactically correct
    public boolean advance() {
        while (in.hasNextLine()) {
            command = in.nextLine();
            if (!command.equals("") && command.charAt(0)!='/') {
                if (command.indexOf('/')!=-1) {
                    command = command.substring(0, command.indexOf('/'));
                }
                command = command.trim();
                return true;
            }
        }
        in.close();
        return false;
    }

    // 0: A_COMMAND, 1: C_COMMAND, 2: L_COMMAND
    public int commandType() {
        if (command==null) { throw new NullPointerException("No command to parse."); }
        if (command.charAt(0)=='@') { return 0; }
        else if (command.charAt(0)=='(') {return 2;}
        else {return 1;}
    }

    public String symbol() {
        if (command.charAt(0)=='@') {
            return command.substring(1, command.length());
        } else {
            return command.substring(1, command.length()-1);
        }
    }

    public String dest() {
        int pos = command.indexOf('=');
        if (pos==-1) {
            return null;
        } else {
            return command.substring(0, pos);
        }
    }

    public String comp() {
        int pos = command.indexOf('=');
        if (pos==-1) {
            return command.substring(0, command.indexOf(';'));
        } else {
            return command.substring(pos+1, command.length());
        }
    }

    public String jump() {
        int pos = command.indexOf(';');
        if (pos==-1) {
            return null;
        } else {
            return command.substring(pos+1, command.length());
        }
    }
}
