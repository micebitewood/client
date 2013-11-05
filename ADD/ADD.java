import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Iterator;
import java.util.Map.Entry;


public class ADD {
    static Socket client;
    static PrintWriter out;
    static BufferedReader in;
    
    private static final String[] programs = {"dlru", "dlur", "drlu", "drul", "dulr", "durl", "ldru", "ldur", "lrdu",
    "lrud", "ludr", "lurd", "rdlu", "rdul", "rldu", "rlud", "rudl", "ruld", "udlr", "udrl", "uldr", "ulrd",
    "urdl", "urld" };
    
    private HashMap<Integer, Integer[]> locations;
    private HashMap<Integer, HashMap<Integer, Character>> edges;
    private HashSet<Integer> remainingNodes;
    private List<Nanomuncher> myNanomunchers;
    private List<Integer> otherNanomunchers;
    private HashMap<Integer, Character> newOpponentNanomunchers;
    private int myScore;
    private int opponentScore;
    private int remainingMunchers;
    private int opponentRemainingMunchers;
    private long remainingTime;
    private boolean firstRound = true;
    private HashSet<Integer> visitNextRound;
    private HashSet<Integer> visited;
    
    public static void main(String[] args) throws UnknownHostException, IOException, InterruptedException {
        if (args.length != 1) {
            System.out.println("java RandomPlayer <port>");
            System.exit(0);
        }
        int port = Integer.parseInt(args[0]);
        ADD player = new ADD(port);
        player.startGame();
    }
    
    public ADD(int port) throws UnknownHostException, IOException {
        client = new Socket("127.0.0.1", port);
        out = new PrintWriter(client.getOutputStream(), true);
        in = new BufferedReader(new InputStreamReader(client.getInputStream()));
        
        locations = new HashMap<Integer, Integer[]>(); //<nodeid, [x,y]>
        edges = new HashMap<Integer, HashMap<Integer, Character>>(); //<fromID, HashMap<toID, direction>>
        remainingNodes = new HashSet<Integer>(); //nodeids of remaining nodes
                
        send("ADD");
        parseData(receive());
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
    
    private void parseData(String data) {
        String[] specs = data.split("\n");
        boolean startNodes = false;
        boolean startEdges = false;
        for (String line : specs) {
            String content = line.trim().toLowerCase();
            if (content.equals(""))
                continue;
            if (content.contains("xloc")) {
                startNodes = true;
            } else if (content.contains("nodeid1")) {
                startEdges = true;
            } else if (startEdges) {
                String[] edgeSpecs = line.split(",");
                int node1 = Integer.parseInt(edgeSpecs[0]);
                int node2 = Integer.parseInt(edgeSpecs[1]);
                if (!edges.containsKey(node1)) {
                    edges.put(node1, new HashMap<Integer, Character>());
                }
                if (!edges.containsKey(node2)) {
                    edges.put(node2, new HashMap<Integer, Character>());
                }
                Integer[] loc1 = locations.get(node1);
                Integer[] loc2 = locations.get(node2);
                if (loc1[0].equals(loc2[0])) {
                    if (loc1[1] - loc2[1] == 1) {
                        edges.get(node1).put(node2, 'u');
                        edges.get(node2).put(node1, 'd');
                    } else {
                        edges.get(node1).put(node2, 'd');
                        edges.get(node2).put(node1, 'u');
                    }
                } else {
                    if (loc1[0] - loc2[0] == 1) {
                        this.edges.get(node1).put(node2, 'l');
                        this.edges.get(node2).put(node1, 'r');
                    } else {
                        this.edges.get(node1).put(node2, 'r');
                        this.edges.get(node2).put(node1, 'l');
                    }
                }
            } else if (startNodes) {
                String[] nodeSpecs = line.split(",");
                Integer[] locs = {Integer.parseInt(nodeSpecs[1]), Integer.parseInt(nodeSpecs[2]) };
                locations.put(Integer.parseInt(nodeSpecs[0]), locs);
                remainingNodes.add(Integer.parseInt(nodeSpecs[0]));
            }
        }
    }
    
    public void startGame() throws IOException, InterruptedException {
    	while (parseStat(receive())) {
            System.out.println("remaining munchers: " + remainingMunchers);
            nextMove();
    	}
    }
    
    public boolean parseStat(String str) {
        if (str.equals("0")) {
            return false;
        }
        String[] stats = str.split("\n");
        
        newOpponentNanomunchers = new HashMap<Integer, Character>(); //new nano's current nodeid, direction took to get there
        String[] munched = stats[0].split(":");
        if (Integer.parseInt(munched[0]) > 0) {
            String[] nodes = munched[1].split(",");
            for (int i = 0; i < nodes.length; i++) {
            	parseMunched(nodes[i]); //update newOpponentNanomunchers with all new Nanos that located at node with at least one edge
            }
        }
        
        myNanomunchers = new ArrayList<Nanomuncher>();
        String[] myMunchers = stats[1].split(":");
        if (Integer.parseInt(myMunchers[0]) > 0) {
            String[] myMuncherDetails = myMunchers[1].split(",");
            for (int i = 0; i < Integer.parseInt(myMunchers[0]); i++) {
                String[] muncher = myMuncherDetails[i].split("/");
                myNanomunchers.add(new Nanomuncher(muncher[1], Integer.parseInt(muncher[0]), Integer
                                                   .parseInt(muncher[2])));
                if (newOpponentNanomunchers.containsKey(Integer.parseInt(muncher[0])))
                	newOpponentNanomunchers.remove(Integer.parseInt(muncher[0]));
            }
        }
        
        otherNanomunchers = new ArrayList<Integer>();
        String[] otherMunchers = stats[2].split(":");
        if (Integer.parseInt(otherMunchers[0]) > 0) {
            String[] otherMuncherDetails = otherMunchers[1].split(",");
            for (int i = 0; i < Integer.parseInt(otherMunchers[0]); i++) {
                otherNanomunchers.add(Integer.parseInt(otherMuncherDetails[i]));
            }
        }
        
        String[] scores = stats[3].split(",");
        myScore = Integer.parseInt(scores[0]);
        opponentScore = Integer.parseInt(scores[1]);
        
        String[] remainingInfo = stats[4].split(",");
        remainingMunchers = Integer.parseInt(remainingInfo[0]);
        opponentRemainingMunchers = Integer.parseInt(remainingInfo[1]);
        remainingTime = Long.parseLong(remainingInfo[2]);
        
        /*
        System.out.println("New opponent nanos: ");
        for (Entry<Integer, Character> entry : newOpponentNanomunchers.entrySet()) {
        	System.out.print("[" + entry.getKey() + "," + entry.getValue()+ "] ");
        	if (!otherNanomunchers.contains(entry.getKey()))
        			System.out.println("***Error with newOpponentNanomunchers ArrayList.");
        }
        System.out.println("\n");
        */
        return true;
    }
    
    public void parseMunched(String munched) {
    	if (munched.contains("/")) {
    		String split[] = munched.split("/");
    		int from = Integer.parseInt(split[0]);
    		int to = Integer.parseInt(split[1]);
    		remainingNodes.remove(from);
    		remainingNodes.remove(to);
    		newOpponentNanomunchers.put(to, edges.get(from).get(to));
    	}
    	else {
    		remainingNodes.remove(Integer.parseInt(munched));
    	}
    }

    private void nextMove() {
    	int numOfMunchers;
    	String munchers;
    	
    	//very first round
    	if (firstRound == true) {
    		firstRound = false;
    		munchers = "0";
    	}
    	//not first round, opponent has no munchers left
    	else if (opponentRemainingMunchers == 0) {
    		numOfMunchers = Math.min(remainingMunchers, remainingNodes.size());
    		munchers = deployMunchersNormal(numOfMunchers);
    	}
    	//not first round, opponent has munchers left (may play it/not)
    	else {
    		numOfMunchers = Math.min(newOpponentNanomunchers.size(), remainingNodes.size());
    		numOfMunchers = Math.min(numOfMunchers, remainingMunchers);
    		//Check
    		if (numOfMunchers == remainingMunchers && numOfMunchers != newOpponentNanomunchers.size()) 
    			System.out.println("***Possible Error in nextMove()");
    		
    		if (numOfMunchers != 0)
    			munchers = deployMunchersAdversariel(numOfMunchers);
    		else
    			munchers = "0";
    	}
    	
    	send(munchers);
    }
    
    public String deployMunchersNormal(int numOfMunchers) {
    	System.out.println("-----deployMunchersNormal(" + numOfMunchers + ")");
    	
    	visitNextRound = new HashSet<Integer>();
    	
    	Iterator<Integer> iterator;
    	
    	StringBuffer sb = new StringBuffer();
    	sb.append(numOfMunchers + ":");
    	
    	int[] nodeids = new int[numOfMunchers];
    	String[] progs = new String[numOfMunchers];
    	int[] lives = new int[numOfMunchers];
    	
    	int nodeid, max;
    	
    	String program = "";
    	String finalProgram = "";
    	HashSet<Integer> added = new HashSet<Integer>();
    	for (int i = 0; i < numOfMunchers; i++) {
    		int min = 1000;
        	int minID = -1;
    		iterator = remainingNodes.iterator();
    		while (iterator.hasNext()) {
    			
    			nodeid = iterator.next();
    			if (added.contains(nodeid))
    				continue;
    			max = 0;
    			program = "";
    			for (int j = 0; j < programs.length; j++) {
        			int temp = lifeOfMuncher(nodeid, programs[j]);
        			if (max < temp) {
        				program = programs[j];
        				max = temp;
        			}
        		}
    			if (max < min) {
    				min = max;
    				minID = nodeid;
    				finalProgram = program;
    			}
    		}
    		nodeids[i] = minID;
    		progs[i] = finalProgram;
    		lives[i] = min;
    		lifeOfMuncher(minID, finalProgram);
    		visitNextRound.addAll(visited);
    		added.add(minID);
    	}
    	/*
    	for (int i = 0; i < numOfMunchers; i++) {
    		nodeid = iterator.next();
    		max = 0;
    		for (int j = 0; j < programs.length; j++) {
    			int temp = lifeOfMuncher(nodeid, programs[j]);
    			if (max < temp) {
    				program = programs[j];
    				max = temp;
    			}
    		}
    		if (max < min) {
    			min = max;
    			minIndex = i;
    		}
    		lives[i] = max;
    		progs[i] = program;
    		nodeids[i] = nodeid;
    	}
    	
    	while (iterator.hasNext()) {
    		nodeid = iterator.next();
    		max = 0;
    		program = "";
    		for (int j = 0; j < programs.length; j++) {
    			int temp = lifeOfMuncher(nodeid, programs[j]);
    			if (max < temp) {
    				program = programs[j];
    				max = temp;
    			}
    		}
    		if (max > min) {
    			lives[minIndex] = max;
    			progs[minIndex] = program;
    			nodeids[minIndex] = nodeid;
    			min = 1000;
    			minIndex = -1;
    			for (int i = 0; i < numOfMunchers; i++) {
    				if (lives[i] < min) {
    					min = lives[i];
    					minIndex = i;
    				}
    			}
    		}
    	}
    	*/
    	for (int i = 0; i < numOfMunchers; i++) {
    		System.out.println("Location=" + nodeids[i] +" Live=" + lives[i] + " Prog=" + progs[i]);
    		sb.append(nodeids[i] + "/" + progs[i] + ",");
    	}
    	return sb.toString().substring(0, sb.length() - 1);
    }
    
    //Problem: May double count a long path if nodes are connected
    public String deployMunchersAdversariel(int numOfMunchers) {
    	System.out.println("-----deployMunchersAdversarial(" + numOfMunchers + ")");
    	visitNextRound = new HashSet<Integer>();
    	Iterator<Integer> iterator;
    	HashSet<Integer> neighbors;
    	String munchers = "";
    	int counter = 0;
    	HashSet<Integer> added = new HashSet<Integer>();
    	for (Entry<Integer, Character> entry : newOpponentNanomunchers.entrySet()) {
    		neighbors = neighborsOfNewOpponentNano(entry.getKey(), entry.getValue());
    		if (neighbors.isEmpty()) {
    			continue;
    		}
    		
    		iterator = neighbors.iterator();
    		
    		int finalMax = 0;
    		String finalProg = "";
    		int finalID = -1;

    		while (iterator.hasNext()) {
    			
    			int nodeid = iterator.next();
    			if (added.contains(nodeid))
    				continue;
    			int max = 0;
    			String maxProg = "";
    			for (int i = 0; i < programs.length; i++) {
    				int temp = lifeOfMuncher(nodeid, programs[i]);
    				if (max < temp) {
    					max = temp;
    					maxProg = programs[i];
    				}
    			}
    			if (finalMax < max) {
    				finalMax = max;
    				finalProg = maxProg;
    				finalID = nodeid;
    			}
    		}
    		lifeOfMuncher(finalID, finalProg);
    		visitNextRound.addAll(visited);
    		added.add(finalID);
    		munchers = munchers + finalID + "/" + finalProg + ",";
    		counter++;
    		System.out.println("Location=" + finalID +" Live=" + finalMax + " Prog=" + finalProg);
    		//check
    		if (finalID == -1 || finalProg.equals("")) {
    			System.out.println("***Error: deployMunchersAdversariel.");
    		}
    	}
    	munchers = counter + ":" + munchers;
    	
    	return munchers.substring(0, munchers.length() - 1);
    }
    
    //Must check for neighbors still remaining
    public HashSet<Integer> neighborsOfNewOpponentNano(Integer oppo, Character prevMove) {
    	HashSet<Integer> neighConsider = new HashSet<Integer>();
		HashMap<Integer, Character> neighbors = edges.get(oppo);
		if (neighbors == null || neighbors.isEmpty())
			return neighConsider;

    	for (Entry<Integer, Character> entry : neighbors.entrySet()) {
    		if (!entry.getValue().equals(prevMove)) {
    			if (remainingNodes.contains(entry.getKey()))
    				neighConsider.add(entry.getKey());
    		}
    	}
    	if (neighConsider.isEmpty()) {
    		for (Entry<Integer, Character> entry : neighbors.entrySet()) {
        		if (entry.getValue().equals(prevMove)) {
        			if (remainingNodes.contains(entry.getKey()))
        				neighConsider.add(entry.getKey());
        		}
        	}
    	}
    	return neighConsider;
    	
    }
    
    public int lifeOfMuncher(Integer nodeid, String program) {
    	visited = new HashSet<Integer>();
    	char[] prog = program.toCharArray();
    	int life = recursiveSearch(nodeid, prog, 0, visited);
    	if (life == -1) {
    		System.out.println("***Error in lifeOfMuncher()");
    	}
    	return life;
    }
    
    public int recursiveSearch(Integer nodeid, char[] prog, int counter, HashSet<Integer> visited) {
    	int initCounter = counter;
    	if (visitNextRound.contains(nodeid))
    		return 0;
    	visited.add(nodeid);
    	
    	HashMap<Integer, Character> neighbors = edges.get(nodeid);
    	
    	if(neighbors == null || neighbors.isEmpty() )
    		return 0;
    	
    	do {
    		for (Entry<Integer,Character> entry: neighbors.entrySet()) {
        		if (remainingNodes.contains(entry.getKey()) && entry.getValue().equals(prog[counter]) && !visited.contains(entry.getKey()) && !visitNextRound.contains(entry.getKey())) {
        			visited.add(entry.getKey());
        			counter = ((++counter) == 4)?0:counter;
        			return 1 + recursiveSearch(entry.getKey(), prog, counter, visited);
        		}
        	}
    		counter = ((++counter) == 4)?0:counter;
    	}while(counter!=initCounter);
    	
    	return 0;
    }
}

class Nanomuncher {
    String program;
    int programCounter;
    int position;// nodeid
    
    public Nanomuncher(String program, int position, int programCounter) {
        this.program = program;
        this.position = position;
        this.programCounter = programCounter;
    }
}