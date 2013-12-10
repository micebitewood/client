rm ./blue
g++ ./main.cpp -o ./blue
javac client.java 
chmod 777 ./*
java client $1 > output &
