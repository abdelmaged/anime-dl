import time
import sys
import re
from logger import logger
from difflib import SequenceMatcher
import requests

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

def similar(a, b):
	return SequenceMatcher(None, a, b).ratio()

def get_response(url):
	if url:
		response = requests.get(url, timeout=60)
		if response.status_code == 200:
			if similar(url, response.url) > 0.8:
				return response