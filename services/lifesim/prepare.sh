if [ -f $1.dump ]; then
	wgdb $1 import $1.dump
fi
