import java.util.ArrayList;
import java.util.HashMap;

class SymbolTable {
    private HashMap<String, Integer> table;
    private int currentpos;


    public SymbolTable() {
        ArrayList<String> symbols = new ArrayList<>();
        ArrayList<Integer> values = new ArrayList<>();

        // Initializing values for registers
        for (int i=0; i<16; i++) {
            symbols.add("R"+i);
            values.add(i);
        }

        // Initializing other pre-defined symbols
        symbols.add("SP");
        symbols.add("LCL");
        symbols.add("ARG");
        symbols.add("THIS");
        symbols.add("THAT");
        symbols.add("SCREEN");
        symbols.add("KBD");

        values.add(0);
        values.add(1);
        values.add(2);
        values.add(3);
        values.add(4);
        values.add(16384);
        values.add(24576);

        table = new HashMap<>();
        for (int i=0; i<symbols.size(); i++) {
            table.put(symbols.get(i), values.get(i));
        }

        currentpos = 16;
    }

    public int addEntryVariable(String symbol) {
        int temp = currentpos;
        table.put(symbol, currentpos++);
        return temp;
    }

    public void addEntryLabel(String symbol, Integer value) {
        table.put(symbol, value);
    }

    public boolean contains(String symbol) {
        return table.containsKey(symbol);
    }

    public Integer getAddress(String symbol) {
        return table.get(symbol);
    }
}
