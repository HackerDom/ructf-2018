if [ -f vol/$1.dump ] then
	wgdb $1 import vol/$1.dump
fi
