
import org.nlogo.headless.HeadlessWorkspace;
public class sample_fires {
    public static void main(String[] argv) {
        HeadlessWorkspace workspace =
            HeadlessWorkspace.newInstance() ;
        try {
            workspace.open(argv[0]);

        	workspace.command("random-seed 0");
            
            for(int i = 0; i < 10000; i++) {
            
            	String k = Double.toString(Math.random() * (75.0 - 45.0) + 45.0);

            	workspace.command("set density " + k);
            	workspace.command("setup");
            	workspace.command("go") ;
            	System.out.println(workspace.report("burned-trees"));
            	System.out.println(k + " " + workspace.report("burned-trees / initial-trees"));
            }
            
        	workspace.dispose();

        }
        catch(Exception ex) {
            ex.printStackTrace();
        }
    }
    
    
}