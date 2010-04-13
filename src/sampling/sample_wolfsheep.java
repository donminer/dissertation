
import org.nlogo.headless.HeadlessWorkspace;
public class sample_wolfsheep {
    public static void main(String[] argv) {
        HeadlessWorkspace workspace =
            HeadlessWorkspace.newInstance() ;
        try {
            workspace.open("nlogo/WolfSheep.nlogo");

        	workspace.command("set grass? true");
            workspace.command("set initial-number-sheep 100");
            workspace.command("set initial-number-wolves 50");   
            
            System.out.println("iiiiidd");
            
            for(int i = 0; i < 2000; i++) {
            
            	// wolf-reproduce
            	String k1 = Double.toString(Math.random() * (8.0 - 2.0) + 2.0);
            	
            	// sheep-reproduce
				String k2 = Double.toString(Math.random() * (12.0 - 2.0) + 2.0);
				
				//wolf-gain-from-food
				String k3 = Double.toString(Math.random() * (30.0 - 15.0) + 15.0);
				
				//sheep-gain-from-food
				String k4 = Double.toString(Math.random() * (6.0 - 3.0) + 3.0);
				
				//grass-regrowth-time
				String k5 = Double.toString(Math.random() * (50.0 - 10.0) + 10.0);


				workspace.command("set wolf-reproduce " + k1);
				workspace.command("set sheep-reproduce " + k2);
				workspace.command("set wolf-gain-from-food " + k3);
				workspace.command("set sheep-gain-from-food " + k4);
				workspace.command("set grass-regrowth-time " + k5);

            	workspace.command("setup");
            	workspace.command("repeat 500 [ go ]");
            	
            	System.out.print(k1 + " " + k2 + " " + k3 + " " + k4 + " " + k5 + " ");
            	String wolves = "" + workspace.report("count wolves");
            	String sheep = "" + workspace.report("count sheep");
            	
            	for(int j = 0; j < 750; j++) {
            		workspace.command("go");
            		wolves += "," + workspace.report("count wolves");
            		sheep += "," + workspace.report("count sheep");
            	}
            	
            	System.out.print(wolves + " " + sheep + "\n");
            	System.err.println(Integer.toString(i) + "/2000");
            }
            
        	workspace.dispose();

        }
        catch(Exception ex) {
            ex.printStackTrace();
        }
    }
    
    
}