// //  main.cpp
//  main.cpp
//
//  Created by YU YUCHIH on 11/2/13.
//  Copyright (c) 2013 YU YUCHIH. All rights reserved.
//

#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <stdio.h>
#include <stdlib.h>
#include <cstdlib>
#include <cstring>
using namespace std;

#define debug(M, ...) printf("================ DEBUG %d: " M "\n", __LINE__, ##__VA_ARGS__)
#define BOARD_X (22)
#define BOARD_Y (12)

int GAME_OVER=0;
int parse(string str, char arr[][10]){
    char *ptr;
    char cstr[100];
    strcpy(cstr, str.c_str());
    ptr = strtok(cstr, "/,:");
    int cnt=0;
    while(ptr!=NULL){
        strcpy(arr[cnt++], ptr);
        ptr = strtok(NULL, "/,:");
    }
    return cnt;
}

//we are blue, opponent is red
enum STAT{DEAD, ALIVE, NEWNUMCHER, MARK};
class graph;
void DFS(graph& g, int dep);
int test_route(graph& g);
int block(graph& g, string& p);
void addanswer(int nodeNum, string program, int& cnt, string& answer);
class node{
	public:
	int x;
	int y;
	int id;
    int scores[4]; //u p l r
    int gidx;
    string programs[4]; //u p l r
	enum STAT status;
    node(){}
	node(int id, int x, int y){
		this->x = x;
		this->y = y;
		this->id = id;
        this->gidx = -1;
        for(int i = 0; i < 4; i++)
        {
            this->scores[i] = -1;
        }
		setStatus(ALIVE);
	}
	void setStatus(enum STAT status){
		this->status = status;
	}
};
class Nanomuncher{
	public:
	string program;
	int programCounter;
	int nodeid;
	Nanomuncher(){
		this->nodeid = -1;
    }
	Nanomuncher(string program, int programCounter, int nodeid){
		this->program = program;
		this->programCounter = programCounter;
		this->nodeid = nodeid;
	}
};

Nanomuncher munchers[20];
class graph{
	public:
	int adj[200][200];
	int nodeNum;
	vector<node> nodes;
	int map[BOARD_X][BOARD_Y]; //map[0][:] map[11][:] map[:][0] map[:][21] are boundaries
    int groupNum;
    int muncher_num;
    int remain_muncher_num;
    int ad_remain_muncher_num;
    int score;
    int ad_score;
    int remain_time;
    int ad_muncher_num;
    //for parsing only
    char arr[10][10];
    int cnt;
    int nodeId;
    int nodeId2;
    int x, y;
    int advNumchers_node[30];
	int first;
	graph(){
		first = 1;
        groupNum = 0;
		for(int i=0; i < 200; ++i){
			for( int j=0; j < 200; ++j){
				adj[i][j] = 0;
			}
		}//zero the edges;
        for(int i = 0; i < BOARD_X; ++i){
            for(int j = 0; j < BOARD_Y; ++j){
                map[i][j] = -1;
            }
        }
		
		string temp;
		bool readNode, readEdge;
		readNode = false;
		readEdge = false;
		
	    getline(cin, temp);
		while(temp.compare("<EOM>")!=0){
            //cout<<temp<<endl;
			if(temp.compare("nodeid,xloc,yloc") == 0){
				readNode = true;
			}
			else if(temp.compare("nodeid1,nodeid2") == 0){
				readEdge = true;
			}
			else if(readEdge){
                cnt = parse(temp, arr);
                if(cnt == 2){
                    nodeId = atoi(arr[0]);
                    nodeId2 = atoi(arr[1]);
	                setEdge(nodeId, nodeId2);
                }
                else{
                    debug("");
                }
			}
			else if(readNode){
                cnt = parse(temp, arr);
                if(cnt == 3){
                    nodeId = atoi(arr[0]);
                    x = atoi(arr[1])+1; // convenient for boundary condition
                    y = atoi(arr[2])+1; // convenient for boundary condition
                    addNode(nodeId, x, y);
					map[x][y] = nodeId;
                }
                else{
                    //debug("");
                }
			}
	        getline(cin, temp);
		}
        //cout<<"-<EOM>"<<endl;
	}
	void addNode(int id, int x, int y){
		node n(id,x,y);
		nodes.push_back(n);
        //printf("addNode: id %d x %d y %d\n", id, x, y);
        
	}
	void setEdge(int node1, int node2){
        // graph is undirected
		adj[node1][node2] = 1;
		adj[node2][node1]= 1;
        //printf("setEdge: node1 %d<->node2 %d\n", node1, node2);
	}
	void clearmark(){
		for(int i=0; i<nodes.size(); ++i){
			if(this->nodes[i].status == MARK){
				this->nodes[i].status = ALIVE;
				this->map[this->nodes[i].x][this->nodes[i].y] = this->nodes[i].id;
			}
		}
	}
	void pnt(){
		cout<<endl;
		for(int i=0; i<12; ++i){
			for(int j=0; j<22; ++j){
				printf("%4d", this->map[j][i]);
			}
			cout<<endl;
		}
		cout<<endl;
		for(int i=0; i<12; ++i){
			for(int j=0; j<22; ++j){
				cout<<this->nodes[map[j][i]].status;
			}
			cout<<endl;
		}
	}
};
int find(graph& g, string& p, int opt){
    int best = 0;
	int bestscore = 0;
    for(int i=0; i<g.nodes.size(); ++i){
		if(g.nodes[i].status != ALIVE) continue;//
        int cnt = 0;
		for(int j=0; j<4; ++j){
			if(g.nodes[i].scores[j]!=-1) cnt++;
		}
		if(cnt >= opt)
        for(int j=0; j<4; ++j){
            if(g.nodes[i].scores[j]>bestscore){
				for(int k=0; k<4; k++){
					if(k==j) continue;
					if(g.nodes[i].scores[k]>bestscore && g.nodes[i].scores[k]<=g.nodes[i].scores[j]){
						bestscore =g.nodes[i].scores[k];
						best =i;
						p = g.nodes[i].programs[j];
					}
                    if(opt==1){
                        bestscore = g.nodes[i].scores[j];
                        best = i;
                        p = g.nodes[i].programs[j];
                        break;
                    }
				}
			}
        }
    }
    return best;
}

void game_parser(graph& g){
    string temp;
    char arr[200][10];//bug!!!
    int cnt;
    string program;
    int nodeid;
    int programCounter;
	
    //int eaten_nodes[200];
    int eaten_num;
	
    //int muncher_num;
	
    //int ad_muncher_num;
	
    //int score;
    //int ad_score;
	
    //int remain_muncher_num;
    //int remain_time;
	
    int possible_game_over = 0;
	
    //current eaten nodes
    getline(cin, temp);
    if(temp.compare("0")==0){
        possible_game_over = 1;
        eaten_num = 0;
    }
    else
    {
        cnt = parse(temp, arr);
        eaten_num = atoi(arr[0]);
		
        cout<<"eaten_num:"<<eaten_num<<endl;
        if(cnt == eaten_num+1){
            for(int i = 1; i < cnt; i++)
            {
				int nodeid = atoi(arr[i]);
				g.map[g.nodes[nodeid].x][g.nodes[nodeid].y] = -1;
                g.nodes[nodeid].status = DEAD;
                //eaten_nodes[i] = nodeid;//EATING NODE STARTS WITH ONE!!
                //cout<<eaten_nodes[i]<<" ";
            }
            //cout<<endl;
        }
        else{
            debug("");
        }
    }
	cout<<"done processing eaten"<<endl;
	
    //munchers
    getline(cin, temp);
	if(temp.compare("<EOM>")==0 && possible_game_over){
        cout<<"game over"<<endl;
		//cout<<"-1"<<endl;
        GAME_OVER = 1;
        return;
    }
    cnt = parse(temp, arr);
    g.muncher_num = atoi(arr[0]);
    if(cnt == 3*g.muncher_num+1){
        for(int i = 1; i+3 <= cnt; i+=3)
        {
            nodeid = atoi(arr[i]);
            program.assign(arr[i+1]);
            programCounter = atoi(arr[i+2]);
            g.map[g.nodes[nodeid].x][g.nodes[nodeid].y] = -1;
			g.nodes[nodeid].status = NEWNUMCHER;
            munchers[(i-1)/3] = Nanomuncher(program, programCounter, nodeid);
            printf("add muncher, nodeid: %d program: %s programCounter: %d\n", nodeid, program.c_str(), programCounter);
        }
    }
    else{
        debug("");
    }
    
    //opponent munchers
    getline(cin, temp);
    cnt = parse(temp, arr);
    g.ad_muncher_num = atoi(arr[0]);
    if(cnt == g.ad_muncher_num+1){
        for(int i = 1; i < cnt; i++){
            g.advNumchers_node[i-1] = atoi(arr[i]);
            int nodeid = g.advNumchers_node[i-1];
			g.map[g.nodes[nodeid].x][g.nodes[nodeid].y] = -1;
			//g.nodes[nodeid].status = NEWNUMCHER;
            g.nodes[nodeid].status = DEAD;
            printf("add ad muncher, nodeid: %d\n", g.advNumchers_node[i-1]);
        }
    }
    else{
        debug("");
    }
    
    //scores
    getline(cin, temp);
    cnt = parse(temp, arr);
    if(cnt == 2)
    {
        g.score = atoi(arr[0]);
        g.ad_score = atoi(arr[1]);
        //printf("score: %d ad_score: %d\n", score, ad_score);
    }
    else{
        debug("");
    }
    
    //remain number of munchers, remain time
    getline(cin, temp);
    cnt = parse(temp, arr);
    if(cnt == 3)
    {
        g.remain_muncher_num = atoi(arr[0]);
        g.ad_remain_muncher_num = atoi(arr[1]);
        g.remain_time= atoi(arr[2]);
        printf("g.remain_muncher_num: %d g.ad_remain_muncher_num: %d g.remain_time: %d\n", g.remain_muncher_num, g.ad_remain_muncher_num, g.remain_time);
    }
    else{
        debug("");
    }
	
    // <EOM>
    getline(cin, temp);
    if(temp.compare("<EOM>")!=0)
	debug("");
    else
    {
		int answercnt =0;
		int move;
		string answer;
		g.clearmark();
		string p;
		
        
		//g.first=0;
		if(g.first == 1 ){
			g.first = 0;
			g.pnt();
			DFS(g,5);
			test_route(g);// calculate the score of each step
			
			move = find(g, p, 2);
			g.nodes[move].status = NEWNUMCHER;//
			addanswer(move, p, answercnt, answer);
			g.clearmark();
			g.pnt();
			DFS(g,30);
			test_route(g);
			//put back
			g.nodes[move].status = ALIVE;
			move = find(g, p, 2);//
			//addanswer(move, p, answercnt, answer);//
		
		}
		else{
			DFS(g,5);
			test_route(g);// calculate the score of each step
			//g.pnt();
			if(g.ad_remain_muncher_num == 0 )
				move = find(g, p, 1);
			else
				move = find(g, p, 2);
		}
		
		addanswer(move, p, answercnt, answer);
		/*
		*/
		
		g.clearmark();
		
		
		//if(g.ad_muncher_num > g.muncher_num + 1){
			move = block(g, p);
			if(move!=-1) addanswer(move, p, answercnt, answer);
		//}
		
		
		
		cout<<"-"<<answercnt<<answer<<endl;
			//cout<<"-1:1/lurd"<<endl;
			//cout<<"-10:2/lurd,4/rdlu,7/ldru,8/urld,9/rdul,10/ludr,11/drul,12/dlur,17/udrl,22/rudl"<<endl;
			//cout<<"-0\n";
			cout<<"-<EOM>"<<endl;
    
	}
	
}
int getnext(graph& g, int dir, int x, int y){
	if(dir==0) y--;
	if(dir==1) y++;
	if(dir==2) x--;
	if(dir==3) x++;
	return g.map[x][y];
}
int block(graph& g, string& p){
	for(int i=0; i<g.ad_muncher_num; ++i){
		int num = g.advNumchers_node[i];
		cout<<"test node"<<num<<endl;
		int cnt = 0;
		int dir;
		for(int j=0; j<4; j++){
			if(g.nodes[num].scores[j] != -1){
				cnt++;
				dir = j;
			}
		}
		cout<<"cnt: "<<cnt<<endl;
        // there is only one way the ad muncher can go
		if(cnt == 1){
			cout<<"found alone"<<endl;
			int nextnum = getnext(g, dir, g.nodes[num].x, g.nodes[num].y);
			cnt = 0;
			for(int j=0; j<4; ++j){
				if(g.nodes[nextnum].scores[j]!=-1){
					cnt++;
					dir = j;
				}
			}
				
			if(cnt == 1){
				cout<<"alone again"<<endl;
				nextnum = getnext(g, dir, g.nodes[nextnum].x, g.nodes[nextnum].y);
				cnt = 0;
				
				for(int j=0; j<4; ++j){
					if(g.nodes[nextnum].scores[j] > 3){//BLOCK NUMBER
						cnt++;
						p = g.nodes[nextnum].programs[j];
					}
				}
				if(cnt>=1){
					cout<<"bb u"<<endl;
					return nextnum;
				}
			}
		}
	}
	return -1;
}
void addanswer(int nodeNum, string program, int& cnt, string& answer){
	cnt++;
	if(answer.length()==0){
		stringstream ss;
		ss<<":"<<nodeNum<<"/"<<program;
		answer = ss.str();
	}
	else{
		cout<<"blocking"<<endl;
		stringstream ss;
		ss<<answer<<","<<nodeNum<<"/"<<program;
		answer = ss.str();
	}
}
int testvalid(graph& g, int x, int y, int nx, int ny){
	if(g.map[nx][ny]==-1) return 0;
	if(g.nodes[g.map[nx][ny]].status == MARK) return 0;
	if(g.adj[g.map[x][y]][g.map[nx][ny]]==0) return 0;
	return 1;
}
void makedead(graph& g, int dep, int nodenum){
	if(g.nodes[nodenum].status == ALIVE  && dep>0){
		printf("making %d dead\n", nodenum);
		g.nodes[nodenum].status = MARK;
		//g.map[g.nodes[nodenum].x][g.nodes[nodenum].y] = -1;
		int x,y;
		x = g.nodes[nodenum].x;
		y = g.nodes[nodenum].y;
		int nextx, nexty;
		
		nextx = g.nodes[nodenum].x +1;
		if(testvalid(g, x,y,nextx, y)) makedead(g, dep-1, g.map[nextx][y]);
		
		nextx = g.nodes[nodenum].x -1;
		if(testvalid(g, x,y,nextx, y)) makedead(g, dep-1, g.map[nextx][y]);
		
		nexty = g.nodes[nodenum].y +1;
		if(testvalid(g, x,y,x, nexty)) makedead(g, dep-1, g.map[x][nexty]);
		
		nexty = g.nodes[nodenum].y -1;
		if(testvalid(g, x,y,x, nexty)) makedead(g, dep-1, g.map[x][nexty]);
	}
	
}

void DFS(graph& g, int dep){
	for(int i=0; i<g.nodes.size(); ++i){
		if(g.nodes[i].status == NEWNUMCHER){
			g.nodes[i].status = ALIVE;
			makedead(g, dep, i);
		}
	}
}

void get_dir(string program, int program_counter, int& dir_x, int& dir_y)
{
    dir_x = 0;
    dir_y = 0;
    if(program.at(program_counter) == 'r')
        dir_x = 1;
    else if(program.at(program_counter) == 'l')
        dir_x = -1;
    else if(program.at(program_counter) == 'u')
        dir_y = -1;
    else if(program.at(program_counter) == 'd')
        dir_y = 1;
}
int dir_idx(int dir_x, int dir_y)
{
    if(dir_x == 1)
        return 3;
    if(dir_x == -1)
        return 2;
    if(dir_y == 1)
        return 1;
    if(dir_y == -1)
        return 0;
    return -1;
}
void idx_dir(int idx, int& dir_x, int& dir_y)
{
    switch(idx){
        case 0:
            dir_x = 0;
            dir_y = -1;
            break;
        case 1:
            dir_x = 0;
            dir_y = 1;
            break;
        case 2:
            dir_x = -1;
            dir_y = 0;
            break;
        case 3:
            dir_x = 1;
            dir_y = 0;
            break;
    }
}
int gen_program_table(string program_sample[24], string dir_sample)
{
    int n = 0;
    int tag[4] = {0,0,0,0};
    string program = "udlr";
    for(int i = 3; i >= 0; i--)
    {
        tag[i] = 1;
        for(int j = 3; j >= 0; j--)
        {
            if(tag[j] == 0)
            {
                tag[j] = 1;
                for(int k = 3; k>=0; k--)
                {
                    if(tag[k] == 0)
                    {
                        tag[k] = 1;
                        for(int l = 3; l>=0; l--)
                        {
                            if(tag[l] == 0)
                            {
                                program[0] = dir_sample[i];
                                program[1] = dir_sample[j];
                                program[2] = dir_sample[k];
                                program[3] = dir_sample[l];
                                program_sample[n] = program;
                                //cout<<n<<":"<<program<<endl;
                                n++;
                            }
                        }
                        tag[k] = 0;
                    }
                }
                tag[j] = 0;
            }
        }
        tag[i] = 0;
    }
}
int find_node_route(graph& g, node& n, string program){
    //cout<<"111 node: "<<n.id<<endl;
    int score = 1;
    int map[BOARD_X][BOARD_Y];
    for(int i = 0; i < BOARD_X; ++i){
        for(int j = 0; j < BOARD_Y; ++j){
            map[i][j] = g.map[i][j];
            //cout<<map[i][j]<<" ";
        }
        //cout<<endl;
    }
    int pc = 0;
    int x = n.x;
    int y = n.y;
    int nx;
    int ny;
    int dir_x;
    int dir_y;
    int find = 0;
    int nodeid;
    int f_dir_x;
    int f_dir_y;
    int first = 0;
    int i;
    do{
        nodeid = map[x][y];
        map[x][y]= -1;
        for(i= 0; i<4; i++){
            //cout<<"2";
            get_dir(program, pc, dir_x, dir_y);
            pc++;
            pc%=4;
            nx = x+dir_x;
            ny = y+dir_y;
            if(map[nx][ny] != -1 && g.adj[nodeid][map[nx][ny]] == 1 && g.nodes[map[nx][ny]].status!=DEAD && g.nodes[map[nx][ny]].status!=MARK){
                if(first == 0)
                {
                    first = 1;
                    f_dir_x = dir_x;
                    f_dir_y = dir_y;
                }
                x = nx;
                y = ny;
                score++;
                break;
            }
            
            
        }
        //cout<<"pc:"<<pc<<endl;
    }while(i < 4);
    if(first)
    {
        int idx = dir_idx(f_dir_x, f_dir_y);
        //cout<<"idx:"<<idx<<endl;
        if(score>n.scores[idx])
        {
            n.scores[idx] = score;
            n.programs[idx] = program;
            //cout<<"scores:"<<n.scores[idx]<<endl;
            //cout<<"program:"<<n.programs[idx]<<endl;
        }
    }
    return score;
}

int find_route(graph& g, int steps[200][24], string program_sample[24]) 
{
    for(int i = 0; i < g.nodes.size(); i++)
    {
        for(int j = 0; j < 24; j++)
        {
            steps[i][j] = 0;
        }
    }

    string program;
    for (std::vector<node>::iterator it = g.nodes.begin() ; it != g.nodes.end(); ++it){
        
		for(int i=0; i<4; ++i)
			it->scores[i] = -1;
		
		//if(g.map[it->x][it->y]!= -1)
        for(int i = 0; i < 24; i++){
            program = program_sample[i];
            steps[it->id][i] = find_node_route(g, *it, program);
            //cout<<steps[it->id][i]<<endl;
        }
	}
}

int test_route(graph& g)
{
    int steps[200][24];
    string dir_sample = "udlr";
    string program_sample[24];
    gen_program_table(program_sample, dir_sample);
    find_route(g, steps, program_sample);
	cout<<endl;
    for(int i = 0; i < g.nodes.size(); i++)
    {
        cout<<"x:"<<g.nodes[i].x-1<<" y:"<<g.nodes[i].y-1<<endl;
        for(int k = 0; k < 4; k++)
        {
            cout<<g.nodes[i].programs[k]<<":"<<g.nodes[i].scores[k]<<" ";
        }
        cout<<endl;
        
        for(int j = 0; j < 24; j++)
        {
            cout<<program_sample[j]<<":"<<steps[i][j]<<" ";
        }
        cout<<endl;
    }
}
int infect_graph(graph& g, int nid)
{
    int new_nid;
    int x;
    int y;
    g.nodes[nid].gidx = g.groupNum;
    for(int i = 0; i < 4; i++)
    {
        idx_dir(i, x, y);
        x += g.nodes[nid].x;
        y += g.nodes[nid].y;
        new_nid = g.map[x][y];
        if(new_nid != -1 && g.adj[nid][new_nid]==1 && g.nodes[new_nid].gidx == -1)
        {
            infect_graph(g, new_nid);
        }
    }
}

int sub_graph(graph& g)
{
    int i;
    for(i = 0; i < g.nodes.size(); i++)
    {
        if(g.nodes[i].gidx == -1)
        {
            infect_graph(g, i);
            g.groupNum++;
        }
    }
}

int test_sub_graph(graph& g)
{
    sub_graph(g);
    for(int i = 0; i < g.nodes.size(); i++)
    {
        if(g.nodes[i].gidx == 0)
        {
            cout<<"nodeid:"<<i<<" x:"<<g.nodes[i].x<<" y:"<<g.nodes[i].y<<endl;
        }
    }
}
int main(int argc, const char * argv[])
{
    static graph g;
    test_sub_graph(g);
    //test_route(g);

	while(!GAME_OVER){
		game_parser(g);
	}
    return 0;
}

