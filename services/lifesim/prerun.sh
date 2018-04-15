./prepare.sh 1234
./prepare.sh 4321 

./run.sh 8085 & 
./run.sh 8086 & 
./run.sh 8087 & 
./dump.sh 1234 & 
./dump.sh 4321 &

wait
