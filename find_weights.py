import os
import subprocess
import sys

# arg1 = sys.argv[1]
# arg2 = sys.argv[2]

def increment_array(arr):
	n = len(arr)
	curr=0
	while(arr[curr]==50):
		arr[curr]=-50
		curr+=1
	arr[curr]+=25


weights = [-50]*4
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