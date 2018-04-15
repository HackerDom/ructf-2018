while true; do
	sleep 60
	wgdb $1 export vol/$1.dump.tmp
	mv vol/$1.dump{.tmp,}
done
