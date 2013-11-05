

public class Node {
	
	public static int count=0;
	
	public int id;
	
	public int x;
	public int y;
	
	public int color = 0;
	
	public boolean eaten; //false if still available
	
	public Nanomuncher N; //null for empty node
	
	Node up;
	Node down;
	Node right;
	Node left;
	
	
	public Node(){
		this.id = count++;
		this.eaten = false;
		this.up= null;
		this.down= null;
		this.left= null;
		this.right= null;
	
	}
	
	public Node(Node n){
		this.id = n.id;
		this.eaten = n.eaten;
		this.up= n.up;
		this.down= n.down;
		this.left= n.left;
		this.right= n.right;
	
	}
	
	public Node(int x,int y){
		this.id = count++;
		this.x = x;
		this.y = y;
		this.eaten = false;
		this.up= null;
		this.down= null;
		this.left= null;
		this.right= null;
	}

	public Node(int id,int x,int y){
		this.id = id;
		this.x = x;
		this.y = y;
		this.eaten = false;
		this.up= null;
		this.down= null;
		this.left= null;
		this.right= null;
	}


}
