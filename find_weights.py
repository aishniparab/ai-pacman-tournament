import os
import subprocess
import sys

# arg1 = sys.argv[1]
# arg2 = sys.argv[2]
weights_TOT = [-1000,100,350,-10,-100,0,0,-350,500,-50,-2]
weights = [-1000,100,350,-10,-100,0,0,-350,500,-50,-2]

import random
def increment_array(arr):
	for i in range(len(arr)):
		arr[i] = weights_TOT[i]+random.choice(range(-100,150,50))
	# n = len(arr)
	# curr=0
	# while(arr[curr]==10):
	# 	arr[curr]=-10
	# 	curr+=1
	# arr[curr]+=25
import random

increment_array(weights)
# random.seed
# print(random.choice(range(-100,100,20)))
# weights = [-10]*4
# weights[len(weights)-2]=arg1
# weights[len(weights)-1]=arg2
for _ in range(5**8):
	scores = 0
	for i in range(3):
		p = subprocess.Popen(["python", "capture.py", "-r", "myTeam", "-q", str(weights), "|","grep","Average Score"],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out,err = p.communicate()
		scores+=int(out.split("Scores:        ")[1].split()[0])
	avg_score = scores/3
	print(avg_score, weights)
	f = open("weights.txt","a")
	f.write(str(avg_score))
	f.write(" ")
	f.write(str(weights))
	f.write("\n")
	f.close()
	# print "echo '" + str(avg_score) +" "+str(weights)+"'"+" >> ./weights.txt"
	# os.system("echo '" + str(avg_score) +" "+str(weights)+"'"+" >> 'weights.txt'")
	# f = open("weights.txt","w")
	# f.write(str(avg_score) + " " + str(weights))
	# f.close()
	increment_array(weights)