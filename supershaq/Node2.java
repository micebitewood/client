
public class Node2 {
	
public static int count=0;
	
	public int id;
	
	public int x;
	public int y;
	
	public int color = 0;
	
	public boolean eaten; //false if still available
	
	public Nanomuncher N; //null for empty node
	
	int up;
	int down;
	int left;
	int right;
	
	
	public Node2(){
		this.id = count++;
		this.eaten = false;
		this.up= -1;
		this.down= -1;
		this.left= -1;
		this.right= -1;
	
	}
	
	public Node2(Node2 n){
		this.id = n.id;
		this.eaten = n.eaten;
		this.up= n.up;
		this.down= n.down;
		this.left= n.left;
		this.right= n.right;
	
	}
	
	public Node2(int x,int y){
		this.id = count++;
		this.x = x;
		this.y = y;
		this.eaten = false;
		this.up= -1;
		this.down= -1;
		this.left= -1;
		this.right= -1;
	}

	public Node2(int id,int x,int y){
		this.id = id;
		this.x = x;
		this.y = y;
		this.eaten = false;
		this.up= -1;
		this.down= -1;
		this.left= -1;
		this.right= -1;
	}

}
