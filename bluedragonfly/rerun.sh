rm ./rblue
g++ ./main_redemption.cpp -o ./rblue
javac rclient.java 
chmod 777 ./*
java rclient $1
