prun=0
pop=(70 80 90 100)
plive=(0.05 0.1 0.2 0.3 0.4)
epochs=(150 200 250 300 350)
for p in "${pop[@]}"
do
	l_c=0
	for l in "${plive[@]}"
	do
		prun=$((prun+1))
		l_c=$((l_c+1))
		python3 game_of_life.py $prun $p ${epochs[$l_c]} $l & 
	done
done