import java.io.BufferedReader;
import java.io.Console;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;

public class snm2 {
	
	static Socket client;
	static PrintWriter out;
	static BufferedReader in;

	private static final String[] programs = { "dlru", "dlur", "drlu", "drul",
			"dulr", "durl", "ldru", "ldur", "lrdu", "lrud", "ludr", "lurd",
			"rdlu", "rdul", "rldu", "rlud", "rudl", "ruld", "udlr", "udrl",
			"uldr", "ulrd", "urdl", "urld" };

	public List<Node2> remainingNodesList = new ArrayList<Node2>();
	public boolean[][] edgeMatrix; 
	
	private List<Nanomuncher> myNanomunchers;
	private List<Nanomuncher> otherNanomunchers;

	private int myScore;
	private int opponentScore;

	private int myRemainingMunchers;
	private int hisRemainingMunchers;
	private long remainingTime;

	public snm2(int port) throws UnknownHostException, IOException {

		client = new Socket("127.0.0.1", port);
		out = new PrintWriter(client.getOutputStream(), true);
		in = new BufferedReader(new InputStreamReader(client.getInputStream()));

		send("SuperShaq");
		parseData(receive());
	}

	private void parseData(String data) {
		String[] specs = data.split("\n");
		boolean startNodes = false;
		boolean startEdges = false;
		edgeMatrix = null;
		
		for (String line : specs) {
			String content = line.trim().toLowerCase();
			if (content.equals(""))
				continue;
			
			if (content.contains("xloc")) {
				startNodes = true;
			
			} else if (content.contains("nodeid1")) {
				startEdges = true;
				edgeMatrix = new boolean[remainingNodesList.size()][remainingNodesList.size()];
				//Arrays.fill(edgeMatrix, Boolean.FALSE);
			
			} else if (startEdges) {
				String[] edgeSpecs = line.split(",");
				
				int nodeId1 = Integer.parseInt(edgeSpecs[0]);
				int nodeId2 = Integer.parseInt(edgeSpecs[1]);
				
				edgeMatrix[nodeId1][nodeId2] = true;
				edgeMatrix[nodeId2][nodeId1] = true;
				
				Node2 a = remainingNodesList.get(nodeId1);
				Node2 b = remainingNodesList.get(nodeId2);
				
				if (a.x == b.x) {
					if (a.y - b.y == 1) {
						a.up = b.id;
						b.down = a.id;				
					} else {
						a.down = b.id;
						b.down = a.id;
					}
				} else {
					if (a.x - b.x == 1) {
						a.left = b.id;
						b.right  = a.id;
					} else {
						a.right = b.id;
						b.left  = a.id;
					}
				}
			} else if (startNodes) {
				String[] nodeSpecs = line.split(",");
				int id = Integer.parseInt(nodeSpecs[0]);
				int x = Integer.parseInt(nodeSpecs[1]);
				int y = Integer.parseInt(nodeSpecs[2]);
				
				Node2 n = new Node2(id,x,y);
				
				remainingNodesList.add(n);
				
				//Board.nodes[x][y] = new Node2(id,x,y);
				
			}
		}
	}

	public boolean parseStat(String str) {
		if (str.equals("0")) {
			return false;
		}
		String[] stats = str.split("\n");
		String[] munched = stats[0].split(":");
		if (Integer.parseInt(munched[0]) > 0) {
			String[] nodes = munched[1].split(",|/");
			for (int i = 0; i < Integer.parseInt(munched[0]); i++) {
				remainingNodesList.get(Integer.parseInt(nodes[i])).eaten = true;
			}
		}
		
		myNanomunchers = new ArrayList<Nanomuncher>();
		String[] myMunchers = stats[1].split(":");
		if (Integer.parseInt(myMunchers[0]) > 0) {
			String[] myMuncherDetails = myMunchers[1].split(",");
			for (int i = 0; i < Integer.parseInt(myMunchers[0]); i++) {
				String[] muncher = myMuncherDetails[i].split("/");
			//	myNanomunchers.add(new Nanomuncher(muncher[1],
		//		remainingNodesList.get(Integer.parseInt(muncher[0])),
			//	Integer.parseInt(muncher[2])));
			}
		}
		otherNanomunchers = new ArrayList<Nanomuncher>();
		String[] otherMunchers = stats[2].split(":");
		if (Integer.parseInt(otherMunchers[0]) > 0) {
			String[] otherMuncherDetails = otherMunchers[1].split(",");
			for (int i = 0; i < Integer.parseInt(otherMunchers[0]); i++) {
		//		otherNanomunchers.add(new Nanomuncher(
		//		remainingNodesList.get(Integer.parseInt(otherMuncherDetails[i]))));
			}
		}
		
		String[] scores = stats[3].split(",");
		myScore = Integer.parseInt(scores[0]);
		opponentScore = Integer.parseInt(scores[1]);
		String[] remainingInfo = stats[4].split(",");
		myRemainingMunchers = Integer.parseInt(remainingInfo[0]);
		hisRemainingMunchers = Integer.parseInt(remainingInfo[1]);
		remainingTime = Long.parseLong(remainingInfo[2]);
		return true;
	}

	public String receive() throws IOException {
		StringBuffer sb = new StringBuffer();
		String temp;
		while (!(temp = in.readLine()).equalsIgnoreCase("<EOM>")) {
			sb.append(temp + "\n");
		}
		sb.deleteCharAt(sb.length() - 1);
		System.out.println("receive:");
		System.out.println(sb.toString());
		return sb.toString();
	}

	public void send(String str) {
		System.out.println("send:");
		out.println(str);
		System.out.println(str);
		out.println("<EOM>");
		System.out.println("<EOM>");
	}

	public void startGame() throws IOException, InterruptedException {
		while (parseStat(receive())) {
			System.out.println("remaining munchers: " + myRemainingMunchers);
			//Thread.sleep(500);
			strategy2();
		}
	}
	
	
	
	//write your strategies here as functions. 
	public void strategy1() {
	
		for( int i = 0; i<remainingNodesList.size();i++){
			if(!remainingNodesList.get(i).eaten){
				send("1:"+i+"/"+"rlud");
			}
		}
		
	}
	
	
	
	public void strategy2() {
	
		List<List<Node2>> valency = new ArrayList<List<Node2>>(4);
		
		List<Node2> v4 = new ArrayList<Node2>();
		List<Node2> v3 = new ArrayList<Node2>();
		List<Node2> v2 = new ArrayList<Node2>();
		
		for(Node2 i : remainingNodesList){
			//System.out.println("entering loop1");
			int temp = 0;
			
			if(i.eaten == true){
				continue;
			}
			
			if(i.up != -1 && remainingNodesList.get(i.up).eaten == false)
				temp++;
			
			if(i.down != -1 && remainingNodesList.get(i.down).eaten == false)
				temp++;
			
			if(i.right != -1 && remainingNodesList.get(i.right).eaten == false)
				temp++;
			
			if(i.left != -1 && remainingNodesList.get(i.left).eaten == false)
				temp++;
			
			if(temp == 4)
				v4.add(i);
			
			if(temp == 3)
				v3.add(i);
			
			if(temp == 2)
				v2.add(i);
			
			//System.out.println("exiting loop1:");
			
		}
		
		System.out.println("v4 : "+v4.toString());
		System.out.println("v3 : "+v3.toString());
		System.out.println("v2 : "+v2.toString());
		
		Console console = System.console();
		String input = console.readLine("Enter input:");
		
		valency.add(v4);
		valency.add(v3);
		valency.add(v2);
		
		
		int maxNodeId = 0;
		ProgSteps maxProg = new ProgSteps();
		maxProg.prog = "uldr";
		maxProg.steps = 0;
		
		if(v4.size()>0){
			for(Node2 i: v4){
				System.out.println("Entering Loop2");
				ProgSteps prog = getMaxProg(i);
				if(prog.steps > maxProg.steps){
					maxProg = prog;
					maxNodeId = i.id;
				}
				//System.out.println("Exiting loop2");
				//System.out.println("max steps:" + maxProg.steps + " max prog: "+ maxProg.prog);
			}
		}
		
		else{ 
			if(v3.size()>0){
				System.out.println("Entering Loop3");
				for(Node2 i: v3){
					ProgSteps prog = getMaxProg(i);
					if(prog.steps > maxProg.steps){
						maxProg = prog;
						maxNodeId = i.id;
					}
				}
			}
			else{
				if(v2.size()>0){
					System.out.println("Entering Loop4");
					for(Node2 i: v2){
						ProgSteps prog = getMaxProg(i);
						if(prog.steps > maxProg.steps){
							maxProg = prog;
							maxNodeId = i.id;
						}
					}
				}
			}
		}
		
		send("1:"+maxNodeId+"/"+maxProg.prog);
		
	}

	private ProgSteps getMaxProg(Node2 org) {
		ProgSteps a = new ProgSteps();
		a.prog = "urdl";
		a.steps = 0;
		
		for(String i : programs){
			
			List<Node2> nodeList = new ArrayList<Node2>();
			
			for(Node2 y : remainingNodesList){
				Node2 nodee = new Node2(y);
				nodeList.add(nodee);
			}
			Node2 n= nodeList.get(org.id);
			int counter = 0;
			int steps = 0;
			int flag = 0;
			
			System.out.println("Entering inner Loop1");
			n.eaten = true;
			while(flag != 4){
				
				System.out.println("Entering inner Loop2, flag : " + flag);
				
				if(i.charAt(counter) == 'u'){
					if(n.up != -1 && nodeList.get(n.up).eaten == false){
						nodeList.get(n.up).eaten = true;
						steps++;
						flag = 0;
					}
					else{
						flag++;
					}	
				}
				if(i.charAt(counter) == 'd'){
					if(n.down != -1 && nodeList.get(n.down).eaten == false){
						nodeList.get(n.down).eaten = true;
						steps++;
						flag = 0;
					}
					else{
						flag++;
					}
				}
				if(i.charAt(counter) == 'l'){
					if(n.left != -1 && nodeList.get(n.left).eaten == false){
						 nodeList.get(n.left).eaten = true;
						steps++;
						flag = 0;
					}
					else{
						flag++;
					}
				}
				if(i.charAt(counter) == 'r'){
					if(n.right != -1 && nodeList.get(n.right).eaten == false){
						nodeList.get(n.right).eaten = true;
						steps++;
						flag = 0;
					}
					else{
						flag++;
					}
				}
				counter = (counter+1)%4;
			}
			if(steps > a.steps){
				a.steps = steps;
				a.prog = i;
			}
			
		}
		
		return a;
	}

	public void strategy3() {
	
		
		
	}
	
	public class ProgSteps{
		String prog;
		int steps;
	}


	public static void ain(String[] args) throws UnknownHostException,
			IOException, InterruptedException {

		if (args.length != 1) {
			System.out.println("java RandomPlayer <port>");
			System.exit(0);
		}

		int port = Integer.parseInt(args[0]);
		snm2 player = new snm2(port);
		player.startGame();
	}

}
