while true; do
	sleep 60
	wgdb $1 export $1.dump.tmp
	mv $1.dump.tmp $1.dump
done
