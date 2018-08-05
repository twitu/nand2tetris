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
        if (jumpmnemonic==null) return "000";

        switch (jumpmnemonic) {
            case "JGT":
                return "001";
            case "JEQ":
                return "010";
            case "JGE":
                return "011";
            case "JLT":
                return "100";
            case "JNE":
                return "101";
            case "JLE":
                return "110";
            case "JMP":
                return "111";
                default:
                    return "000";
        }
    }

    public static String comp(String compmnemonic) {
        if (compmnemonic==null) {
            return "0000000";
        } else {
            if (compmnemonic.indexOf('A')!=-1) {
                switch (compmnemonic) {
                    case "A":
                        return "0110000";
                    case "!A":
                        return "0110001";
                    case "-A":
                        return "0110011";
                    case "A+1":
                        return "0110111";
                    case "A-1":
                        return "0110010";
                    case "D+A":
                        return "0000010";
                    case "D-A":
                        return "0010011";
                    case "A-D":
                        return "0000111";
                    case "D&A":
                        return "0000000";
                    case "D|A":
                        return "0010101";
                        default:
                            return "0000000";
                }
            } else if (compmnemonic.indexOf('M')!=-1) {
                switch (compmnemonic) {
                    case "M":
                        return "1110000";
                    case "!M":
                        return "1110001";
                    case "-M":
                        return "1110011";
                    case "M+1":
                        return "1110111";
                    case "M-1":
                        return "1110010";
                    case "D+M":
                        return "1000010";
                    case "D-M":
                        return "1010011";
                    case "M-D":
                        return "1000111";
                    case "D&M":
                        return "1000000";
                    case "D|M":
                        return "1010101";
                        default:
                            return "0000000";
                }
            } else {
                switch (compmnemonic) {
                    case "0":
                        return "0101010";
                    case "1":
                        return "0111111";
                    case "-1":
                        return "0111010";
                    case "D":
                        return "0001100";
                    case "!D":
                        return "0001101";
                    case "-D":
                        return "0001111";
                    case "D+1":
                        return "0011111";
                    case "D-1":
                        return "0001110";
                        default:
                            return "0000000";
                }
            }
        }
    }
}
