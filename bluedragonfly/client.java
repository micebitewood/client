import java.io.*;
import java.net.*;
import java.util.*;
public class client {
	//static String endmsg = "<EOM>";
	static String proName = "./blue";
	static String host = "127.0.0.1";
	static int port;
	static Socket sock = null;
	static PrintWriter out = null;
	static BufferedReader in = null;
	static String teamname = "Blue Dragonfly\n<EOM>";
	static int M, N;
	static char turn;
	public static String readData(BufferedReader in) throws IOException{
		String s = null;
		String line = null;
		while((line = in.readLine()) != null)
			s += line;
		return s;
	}
	
	public static void sendText(PrintWriter out, String text){
		out.println(text);
	}
	  public static void main(String[] args) throws IOException{
		  //String proName = "./a.out";
		  try{
			  //port = args[0];
			  //turn = args[0].charAt(0);
			  port = Integer.parseInt(args[0]);
			  //build socket
			  System.out.println("Connecting");
			  sock = new Socket(host, port);
			  out = new PrintWriter(sock.getOutputStream(), true);
			  in = new BufferedReader(new InputStreamReader(sock.getInputStream()));
			  
			  //connected
			  System.out.println("Connected!!");
			  
			  //get server welcome message
			  //String data = in.readLine();
			  //System.out.printf("%s\n", data);
			  
			  //send team name
			  sendText(out, teamname);
			  System.out.println("Sending Teamname!!");
			  
			  //execute program

			Runtime runtime = Runtime.getRuntime();
			Process process = runtime.exec("./blue");
			BufferedReader inexe = new BufferedReader(new InputStreamReader(process.getInputStream()));	
			PrintWriter outexe = new PrintWriter(process.getOutputStream(), true);
			
			
			System.out.println("Reading Data");
			  String line = in.readLine();
			  while(line.equals("<EOM>") != true){
				  outexe.println(line);
				  System.out.println("server: " + line);
				  line = in.readLine();
			  }
			  outexe.println(line);
			  System.out.println("server: " + line);
			boolean gameover = false;
			  while(!gameover){
				  
				  System.out.println("Reading Input From Server");
				  line = in.readLine();
				  System.out.println("server: " + line);
				  while(line.equals("<EOM>") != true){
					  outexe.println(line);
					  line = in.readLine();
					  System.out.println("server: " + line);
				  }
				  outexe.println(line);
				  //System.out.println("server: " + line);
				  
				  System.out.println("Waiting for Program!!");
				  line = inexe.readLine();
				  System.out.println("Reading something!!\n" + line);
				  while(line.equals("-<EOM>") != true){
					  if(line.length()==0){
						  line = inexe.readLine();
						  continue;
					  }
					  if(line.charAt(0)!='-'){//only print out message
						  System.out.println(line);
						  if(line.equals("game over") == true){
							  gameover = true;
							  break;
						  }
					  }
					  else{
						  out.println(line.substring(1));	
						  System.out.println("send" + line.substring(1) + "to server");
					  }
						  //System.out.println(line);
					  line = inexe.readLine();
					  //System.out.println("debug print\n" + line );
				  }
				  if(!gameover){
					  	out.println(line.substring(1));
				  		System.out.println("send" + line.substring(1) + "to server");
				  		//System.out.println(line);
				  }
				 }
		  }catch (UnknownHostException e) {
				System.err.printf("Unknown host: %s:%d\n",host,port);
				System.exit(1);
		} 
		  catch(IOException e){
			  System.out.println(e);
			  System.exit(1);
		  }
	  }//end main method
}//end class

