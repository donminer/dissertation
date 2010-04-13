
import org.nlogo.headless.HeadlessWorkspace;
public class sample_flocking {
    public static void main(String[] argv) {
        HeadlessWorkspace workspace =
            HeadlessWorkspace.newInstance() ;
        try {
            workspace.open("nlogo/Flocking.nlogo");

        	workspace.command("random-seed 0");
            workspace.command("set vision 10.0");
            workspace.command("set minimum-separation 1.0");   
            workspace.command("set population 300");
            
            System.out.println("iiid");
            
            for(int i = 0; i < 2000; i++) {
            
            	String k1 = Double.toString(Math.random() * (20.0 - 1.0) + 1.0);
				String k2 = Double.toString(Math.random() * (20.0 - 1.0) + 1.0);
				String k3 = Double.toString(Math.random() * (20.0 - 1.0) + 1.0);

				workspace.command("set max-align-turn " + k1);
				workspace.command("set max-cohere-turn " + k2);
				workspace.command("set max-separate-turn " + k3);
            	workspace.command("setup");
            	workspace.command("repeat 200 [ go ]");
            	
            	System.out.print(k1 + " " + k2 + " " + k3 + " " + workspace.report("dist0"));
            	for(int j = 0; j < 10; j++) {
            		workspace.command("go");
            		System.out.print("," + workspace.report("dist0"));
            	}
            	
            	System.out.print("\n");
            	System.err.println(Integer.toString(i) + "/2000");
            }
            
        	workspace.dispose();

        }
        catch(Exception ex) {
            ex.printStackTrace();
        }
    }
    
    
}