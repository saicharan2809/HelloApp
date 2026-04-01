public class HelloApp1 {
    public static void main(String[] args) {
        StringBuilder nameBuilder = new StringBuilder("World");
        for (int i = 0; i < args.length; i++) {
            nameBuilder.append(args[i]);
            if (i<args.length-1) {
                nameBuilder.append(" ");
            }
        }
        System.out.println("Hello, " + nameBuilder.toString() + "!");
    }

}
