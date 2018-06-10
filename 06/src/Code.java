public class Code {
    public static String dest(String destmnemonic) {
        char[] seq = {'0','0','0'};
        if (destmnemonic==null) {
            return "000";
        } else {
            for (int i=0; i<destmnemonic.length(); i++) {
                if (destmnemonic.charAt(i)=='A') {
                    seq[0] = '1';
                } else if (destmnemonic.charAt(i)=='M'){
                    seq[2] = '1';
                } else {
                    seq[1] = '1';
                    break;
                }
            }

            return new String(seq);
        }
    }

    public static String jump(String jumpmnemonic) {
        if (jumpmnemonic==null) {
            return "000";
        } else if (jumpmnemonic.equals("JGT")) {
            return "001";
        } else if (jumpmnemonic.equals("JEQ")) {
            return "010";
        } else if (jumpmnemonic.equals("JGE")) {
            return "011";
        } else if (jumpmnemonic.equals("JLT")) {
            return "100";
        } else if (jumpmnemonic.equals("JNE")) {
            return "101";
        } else if (jumpmnemonic.equals("JLE")) {
            return "110";
        } else if (jumpmnemonic.equals("JMP")) {
            return "111";
        }
        return "000";
    }

    public static String comp(String compmnemonic) {
        if (compmnemonic==null) {
            return "0000000";
        } else {
            if (compmnemonic.indexOf('A')!=-1) {
                if (compmnemonic.equals("A")) {return "0110000";}
                if (compmnemonic.equals("!A")) {return "0110001";}
                if (compmnemonic.equals("-A")) {return "0110011";}
                if (compmnemonic.equals("A+1")) {return "0110111";}
                if (compmnemonic.equals("A-1")) {return "0110010";}
                if (compmnemonic.equals("A-1")) {return "0110010";}
                if (compmnemonic.equals("D+A")) {return "0000010";}
                if (compmnemonic.equals("D-A")) {return "0010011";}
                if (compmnemonic.equals("A-D")) {return "0000111";}
                if (compmnemonic.equals("D&A")) {return "0000000";}
                if (compmnemonic.equals("D|A")) {return "0010101";}
            } else if (compmnemonic.indexOf('M')!=-1) {
                if (compmnemonic.equals("M")) {return "1110000";}
                if (compmnemonic.equals("!M")) {return "1110001";}
                if (compmnemonic.equals("-M")) {return "1110011";}
                if (compmnemonic.equals("M+1")) {return "1110111";}
                if (compmnemonic.equals("M-1")) {return "1110010";}
                if (compmnemonic.equals("M-1")) {return "1110010";}
                if (compmnemonic.equals("D+M")) {return "1000010";}
                if (compmnemonic.equals("D-M")) {return "1010011";}
                if (compmnemonic.equals("M-D")) {return "1000111";}
                if (compmnemonic.equals("D&M")) {return "1000000";}
                if (compmnemonic.equals("D|M")) {return "1010101";}
            } else {
                if (compmnemonic.equals("0")) {return "0101010";}
                if (compmnemonic.equals("1")) {return "0111111";}
                if (compmnemonic.equals("-1")) {return "0111010";}
                if (compmnemonic.equals("D")) {return "0001100";}
                if (compmnemonic.equals("!D")) {return "0001101";}
                if (compmnemonic.equals("-D")) {return "0001111";}
                if (compmnemonic.equals("D+1")) {return "0011111";}
                if (compmnemonic.equals("D-1")) {return "0001110";}
            }
        }
        return "0000000";
    }
}
