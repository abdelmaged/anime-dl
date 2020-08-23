import time
import sys
import re
from logger import logger

def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		timeformat = '{:02d}:{:02d}'.format(mins, secs)
		logger.Print(timeformat, end='\r')
		time.sleep(1)
		t -= 1
	print('', end='\r')

def str2List(_str):
	strList = _str.strip().split(",")
	intList = []
	for s in strList:
		rngStr = s.strip().split("-")
		rngNum = [int(x) for x in rngStr]
		rngLen = len(rngNum)
		if rngLen == 1:
			rngNum.append(rngNum[0])
		elif rngLen == 2 and rngNum[0] <= rngNum[1]:
			pass
		else:
			print("Error: Ignoring range {0}. Invalid format.".format(rngStr), file=sys.stderr)
		intList.append(rngNum)
	return sorted(intList)

def js2json(js):
	pattern = r"([a-zA-Z_][a-zA-Z_0-9]*)\s*\:"	
	repl = lambda match: '"{}":'.format(match.group(1))
	return re.sub(pattern, repl, js)
