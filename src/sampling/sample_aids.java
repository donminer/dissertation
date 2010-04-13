
import org.nlogo.headless.HeadlessWorkspace;
public class sample_aids {
    public static void main(String[] argv) {
        HeadlessWorkspace workspace =
            HeadlessWorkspace.newInstance() ;
        try {
            workspace.open("nlogo/AIDS.nlogo");

        	workspace.command("set initial-people 300");
            workspace.command("set average-coupling-tendency 3");
            workspace.command("set average-commitment 2");   
            
            System.out.println("iidd");
            
            for(int i = 0; i < 2000; i++) {
            
            	// average-condom-use
            	String k1 = Double.toString(Math.random() * (10.0 - 0.0) + 0.0);
            	
            	// average-test-frequency
				String k2 = Double.toString(Math.random() * (1.0 - 0.0) + 0.0);


				workspace.command("set average-condom-use " + k1);
				workspace.command("set average-test-frequency " + k2);

            	workspace.command("setup");
            	
            	System.out.print(k1 + " " + k2 + " ");
            	String hivminus = "" + workspace.report("val-hivminus");
            	String hivplus = "" + workspace.report("val-hivplus");
            	
            	while (Double.parseDouble("" + workspace.report("val-hivwhat")) > 0.0) {
            		workspace.command("go");
            		hivminus += "," + workspace.report("val-hivminus");
            		hivplus += "," + workspace.report("val-hivplus");
            	}
            	
            	System.out.print(hivminus + " " + hivplus + "\n");
            	System.err.println(Integer.toString(i) + "/2000");
            }
            
        	workspace.dispose();

        }
        catch(Exception ex) {
            ex.printStackTrace();
        }
    }
    
    
}