

public class Nanomuncher {
	
	int startTime;
	
	String program;
	int programCounter;
	Node presentPosition; 
	int active; //0 for still to use, 1 for alive and eating, -1 for dead
	
	public Nanomuncher() {
		
	}
	
	public Nanomuncher(Node position) {
		this.program = null;
		this.presentPosition = position;
		this.programCounter = -1;
		this.active = 1;
	}
	
	public Nanomuncher(String program, Node position, int programCounter) {
		this.program = program;
		this.presentPosition = position;
		this.programCounter = programCounter;
		this.active = 1;
	}

}
