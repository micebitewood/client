#include <cassert>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

struct Nanomuncher {
	Nanomuncher(int ni, const string &c, int pc_ = -1) :
		node_id(ni),
		code(c),
		pc(pc_) { }

	int node_id;
	string code;
	int pc;
};

struct Node {
	Node(int id_ = -1, int x_ = -1, int y_ = -1, bool m = false, int l = -1, int u = -1, int r = -1, int d = -1) :
		id(id_),
		x(x_),
		y(y_),
		munched(m),
		left(l),
		up(u),
		right(r),
		down(d) { }

	int id;
	int x;
	int y;

	bool munched;

	int left;
	int up;
	int right;
	int down;
};

int get_code_id(const string &);
int get_degree_1(int, vector<Node> &);
int get_degree_2(int, vector<Node> &);

int main(int argc, char ** argv) {
	if (argc != 2) {
		cout << "Incorrect arguments (1 required: <mode>)\n";
		return 1;
	}
	//cout << "starting in mode " << argv[1] << endl;

	int mode = atoi(argv[1]);
	string buffer;
	stringstream ss;

	/* VARIABLES */
	vector<Node> nodes;
	vector<Nanomuncher> my_munchers;
	vector<Nanomuncher> opp_munchers;
	unsigned my_score, opp_score, my_remaining, opp_remaining;
	double time_remaining;

	if (mode == 0) {
		/* PHASE 2 */
		ifstream infile("orange_init.txt");

		// Node format
		getline(infile, buffer);

		// Nodes
		char comma;
		int id, x, y;
		while (infile >> id >> comma >> x >> comma >> y) {
			if (id != nodes.size()) {
				cout << "Warning - Node ID does not match index\n";
			}
			nodes.push_back(Node(id, x, y));
		}
		infile.clear();

		// Edge format
		getline(infile, buffer);

		// Edges
		int id1, id2;
		while (infile >> id1 >> comma >> id2) {
			assert((unsigned)id1 < nodes.size() && (unsigned)id2 < nodes.size());

			int x1 = nodes[id1].x;
			int y1 = nodes[id1].y;
			int x2 = nodes[id2].x;
			int y2 = nodes[id2].y;

			if (x1 == x2) {
				if (y1 < y2) {
					// TODO: Maybe check to ensure that up, down etc. are uninitialized (-1)
					nodes[id1].down = id2;
					nodes[id2].up = id1;
				} else if (y1 > y2) {
					nodes[id1].up = id2;
					nodes[id2].down = id1;
				} else cout << "Warning 01 - attempted to create circular edge\n";
			} else if (y1 == y2) {
				if (x1 < x2) {
					nodes[id1].right = id2;
					nodes[id2].left = id1;
				} else if (x1 > x2) {
					nodes[id1].left = id2;
					nodes[id2].right = id1;
				} else cout << "Warning 02 - attempted to create circular edge\n";
			} else {
				// nodes are not adjacent
				cout << "Warning 03 - attempted to create edge between nonadjacent nodes\n";
			}
		}
		infile.clear();
		infile.close();

	} else {
		ifstream instate("orange_state.txt");
		bool munched;
		int id, x, y, left, up, right, down, num_munched, num_munchers, pc;
		char a, b, c, d, delimiter;

		while (instate >> id >> x >> y >> munched >> left >> up >> right >> down) {
			nodes.push_back(Node(id, x, y, munched, left, up, right, down));
		}
		instate.close();

		ifstream infile("orange_input.txt");

		// Number munched
		getline(infile, buffer);
		ss.str(buffer);
		ss >> num_munched;
		do {
			ss >> delimiter >> id;
			//cout << "Got id: " << id << endl;

			assert((unsigned)id < nodes.size());
			nodes[id].munched = true;
			/* Remove the edges
			if (nodes[id].left != -1) {
				nodes[nodes[id].left].right = -1;
				nodes[id].left = -1;
			}
			if (nodes[id].right != -1) {
				nodes[nodes[id].right].left = -1;
				nodes[id].right = -1;
			}
			if (nodes[id].up != -1) {
				nodes[nodes[id].up].down = -1;
				nodes[id].up = -1;
			}
			if (nodes[id].down != -1) {
				nodes[nodes[id].down].up = -1;
				nodes[id].down = -1;
			}
			*/
		} while (ss.good());
		ss.clear();

		// Player nanomunchers
		getline(infile, buffer);
		ss.str(buffer);
		ss >> num_munchers;
		do {
			ss >> delimiter >> id >> delimiter >> a >> b >> c >> d >> delimiter >> pc;
			//cout << "Got my id: " << id << endl;

			assert((unsigned)id < nodes.size());
			stringstream code;
			code << a << b << c << d;
			my_munchers.push_back(Nanomuncher(id, code.str(), pc));

			code.clear();
		} while (ss.good());
		ss.clear();

		// Opponent nanomunchers
		getline(infile, buffer);
		ss.str(buffer);
		ss >> num_munchers;
		do {
			ss >> delimiter >> id;
			//cout << "Got opp id: " << id << endl;

			assert((unsigned)id < nodes.size());
			opp_munchers.push_back(Nanomuncher(id, ""));
		} while (ss.good());
		ss.clear();

		// Scores
		getline(infile, buffer);
		ss.str(buffer);
		ss >> my_score >> delimiter >> opp_score;
		ss.clear();

		// Remainder details
		getline(infile, buffer);
		ss.str(buffer);
		ss >> my_remaining >> delimiter >> opp_remaining >> delimiter >> time_remaining;

		infile.close();
	}

	/* UPDATE STATE */
	ofstream outstate("orange_state.txt");
	for (vector<Node>::iterator it = nodes.begin(); it != nodes.end(); it++) {
		outstate <<
			it->id << ' ' <<
			it->x << ' ' <<
			it->y << ' ' <<
			it->munched << ' '<< 
			it->left << ' ' <<
			it->up << ' ' <<
			it->right << ' ' <<
			it->down << '\n';
	}
	outstate.close();


	if (mode != 0) {
		/* CALCULATE NEXT MOVES */
		vector<Nanomuncher> spawn;

		//cout << "OPP MUNCHERS SIZE: " << opp_munchers.size() << endl;
		for (vector<Nanomuncher>::iterator it = opp_munchers.begin(); it != opp_munchers.end(); it++) {
			if (spawn.size() >= my_remaining) break;
			int degree = get_degree_1(it->node_id, nodes);
			bool definitely_horizontal = false;
			bool definitely_vertical = false;

			//cout << "Opponent degree: " << degree << endl;
			if (degree == 1) {
				if ((nodes[it->node_id].left != -1 && 
					!nodes[nodes[it->node_id].left].munched) || 
					(nodes[it->node_id].right != -1 && 
					!nodes[nodes[it->node_id].right].munched)) {
						//cout << "D1 - HORIZONTAL" << endl;
						definitely_horizontal = true;
				} else {
					//cout << "D1 - VERTICAL" << endl;
					definitely_vertical = true;
				}
			}
			if (degree == 3) {
				if (nodes[it->node_id].left == -1 || 
					nodes[nodes[it->node_id].left].munched || 
					nodes[it->node_id].right == -1 || 
					nodes[nodes[it->node_id].right].munched) definitely_vertical = true;
				else definitely_horizontal = true;
			}
			if (definitely_horizontal) {
				//cout << "@@@@@@@@@@@@@@@@" << endl;
				if (nodes[it->node_id].left != -1 && !nodes[nodes[it->node_id].left].munched) { 
					int left_and_down = nodes[nodes[it->node_id].left].down;
					if (left_and_down != -1 && !nodes[left_and_down].munched) {
						spawn.push_back(Nanomuncher(left_and_down, "udlr", 0));
						nodes[left_and_down].munched = true;
					}
					nodes[nodes[it->node_id].left].munched = true;
					if (nodes[it->node_id].right != -1 && !nodes[nodes[it->node_id].right].munched) {
						int right_and_up = nodes[nodes[it->node_id].right].up;
						int right_and_down = nodes[nodes[it->node_id].right].down;

						if (right_and_down != -1 && !nodes[right_and_down].munched) {
							spawn.push_back(Nanomuncher(right_and_down, "udlr", 0));
							nodes[right_and_down].munched = true;
						} else if (right_and_up != -1 && !nodes[right_and_up].munched) {
							spawn.push_back(Nanomuncher(right_and_up, "dlru", 0));
							nodes[right_and_up].munched = true;
						}
						nodes[nodes[it->node_id].right].munched = true;
					}
				}
			} else if (nodes[it->node_id].up != -1) nodes[nodes[it->node_id].up].munched = true;
			if (definitely_vertical) {
				//cout << "@@@@@@@@" << endl;
				if (nodes[it->node_id].down != -1 && !nodes[nodes[it->node_id].down].munched) {
					int down_and_left = nodes[nodes[it->node_id].down].left;
					if (down_and_left != -1 && !nodes[down_and_left].munched) {
						spawn.push_back(Nanomuncher(down_and_left, "lrud", 0));
						nodes[down_and_left].munched = true;
					}
					nodes[nodes[it->node_id].down].munched = true;
				}
			}

		}

		int non_adversarial_munchers = (my_remaining - spawn.size()) / 2;
		//cout << "non-adversarial munchers: " << non_adversarial_munchers << endl;
		for (int i = 0; i < non_adversarial_munchers; i++) {
			int max_degree = 0;
			Node best_node;
			for (vector<Node>::iterator it = nodes.begin(); it != nodes.end(); it++) {
				if (spawn.size() >= my_remaining) break;
				if (it->munched) continue;

				int degree = get_degree_1(it->id, nodes);
				if (degree < max_degree) continue;
				if (degree > max_degree) {
					max_degree = degree;
					best_node = *it; 
				} else if (2 * it->x + 2 * it->y > 2 * best_node.x + 2 * best_node.y) best_node = *it;
			}
			if (best_node.down != -1 && !nodes[best_node.down].munched) {
				spawn.push_back(Nanomuncher(best_node.down, "udlr", 0));
				nodes[best_node.id].munched = true;
				nodes[best_node.down].munched = true;
			} else if (best_node.right != -1 && !nodes[best_node.right].munched) {
				spawn.push_back(Nanomuncher(best_node.right, "lrud", 0));
				nodes[best_node.id].munched = true;
				nodes[best_node.right].munched = true;
			} else {
				spawn.push_back(Nanomuncher(best_node.id, "udlr", 0));
				nodes[best_node.id].munched = true;
			}
		}
		/* OUTPUT MOVES */
		ofstream outfile("orange_output.txt");
		//cout << "Spawn size: " << spawn.size() << endl;
		outfile << spawn.size();
		for (vector<Nanomuncher>::iterator it = spawn.begin(); it != spawn.end(); it++) {
			char delimiter = it == spawn.begin() ? ':' : ',';
			outfile << delimiter << it->node_id << '/' << it->code;
		}
		outfile << endl;
		outfile.close();
	}

	//cout << "ending.." << endl;
	//system("pause");
	return 0;
}

int get_degree_1(int id, vector<Node> &nodes) {
	int degree =
		(((nodes[id].left == -1) || nodes[nodes[id].left].munched) ? 0 : 1) +
		(((nodes[id].up == -1) || nodes[nodes[id].up].munched) ? 0 : 1) +
		(((nodes[id].right == -1) || nodes[nodes[id].right].munched) ? 0 : 1) +
		(((nodes[id].down == -1) || nodes[nodes[id].down].munched) ? 0 : 1);
	return degree; // max: 4
}

int get_degree_2(int id, vector<Node> &nodes) {
	int degree =
		(((nodes[id].left == -1) || nodes[nodes[id].left].munched) ? 0 : get_degree_1(nodes[id].left, nodes)) +
		(((nodes[id].up == -1) || nodes[nodes[id].up].munched) ? 0 : get_degree_1(nodes[id].up, nodes)) +
		(((nodes[id].right == -1) || nodes[nodes[id].right].munched) ? 0 : get_degree_1(nodes[id].right, nodes)) +
		(((nodes[id].down == -1) || nodes[nodes[id].down].munched) ? 0 : get_degree_1(nodes[id].down, nodes));
	return degree; // max: 16
}
