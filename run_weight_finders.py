import os
for i in range(-50,75,25):
	for j in range(-50,75,25):
		os.system("nohup python find_weights.py "+str(i) +" "+str(j)+" &")