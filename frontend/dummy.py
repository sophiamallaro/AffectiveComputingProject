
def read(arr):
	file = open("testfile.txt","w")
	for i in arr:
		file.write(str(i) + "\n")
	file.close()