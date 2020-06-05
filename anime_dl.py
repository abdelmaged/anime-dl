#! /usr/bin/python3

import argparse
import requests
import bs4
import re
import sys
import requests
from tqdm import tqdm
import time

logger = None
import time

def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		timeformat = '{:02d}:{:02d}'.format(mins, secs)
		logger.Print(timeformat, end='\r')
		time.sleep(1)
		t -= 1
	print('', end='\r')

class Logger:
	def __init__(self):
		self.tab = 0
	
	def AddTab(self):
		self.tab = self.tab + 1

	def RemoveTab(self):
		if self.tab > 0:
			self.tab = self.tab - 1

	def Print(self, msg, file=sys.stdout, end='\n', tab=True):
		if tab:	
			for i in range(0, self.tab):
				print("  ", end='', file=file)
		print(msg, file=file, end=end)

class Downloader:
	def __init__(self, url, name):
		self.url  = url
		self.filename = name

	def download(self):
		with open(self.filename, 'ab') as f:
			headers = {}
			pos = f.tell()
			if pos:
				headers['Range'] = 'bytes={0}-'.format(pos)
			logger.Print("Getting headers ...")
			response = requests.get(self.url, headers=headers, stream=True, timeout=60)
			total_size = int(response.headers.get('content-length'))
			if pos == total_size:
				return True
			logger.Print("Getting content ...")
			with tqdm(total=total_size+pos, initial=pos, unit_scale=True, unit_divisor=1024, unit='B') as pbar:
				for data in response.iter_content(chunk_size = 1024):
					f.write(data)
					pbar.update(1024)

class GoGoAnime:
	def __init__(self, url):
		self.url = url

	def grab(self, epNum):
		epUrl = self.url + "/episode/episode-" + str(epNum)
		logger.Print("Getting URL ... ")
		epDownloadUrl = self._get_episode_download_url(epUrl)
		if epDownloadUrl != "":
			epUrl = epDownloadUrl
		logger.Print("URL => {0}".format(epUrl))
		return epUrl

	def _get_episode_download_url(self, epUrl):
		html_text = requests.get(epUrl).text
		soup = bs4.BeautifulSoup(html_text, 'html.parser')
		links = soup.find_all('a', text=re.compile(r'^Download$'))
		for link in links:
			return link.get('href')
		return ""

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

def isFiller(epNum, fillerList):
	for rng in fillerList:
		if epNum in range(rng[0], rng[1] + 1):
			return True
	return False

def getEpisodeName(epNum, fillerList):
	name = "episode_{0}".format(epNum)
	if isFiller(epNum, fillerList):
		name = name + "_filler"
	name = name + ".mp4"
	return name

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--url",    help="URL of anime download page", dest="url",         required=True)    
	parser.add_argument("-l", "--list",   help="List of episodes",           dest="list",        default="1-999")
	parser.add_argument("-f", "--filler", help="List of filler episodes",    dest="fillerList",  default="0")
#	parser.add_argument("-o", "--output", help="Output File",                dest="outFileName", default="anime_dl.txt")
	args = parser.parse_args()
	
	url = args.url.lower()
	if "gogoanime" in url:
		server = GoGoAnime(args.url)
	else:
		print("Error: URL not supported! Supported: GoGoAnime", file=sys.stderr)
		return

	global logger
	logger = Logger()
	fillerList = str2List(args.fillerList)
	rngList = str2List(args.list)
	rngLen = len(rngList)
	rngCnt = 1
	epLen  = 0
	epCnt  = 1
	wait   = 60
	for rng in rngList:
		epLen = epLen + (rng[1] - rng[0] + 1) 
	for rng in rngList:
		logger.Print("Processing range ({0}/{1}) => {2} ...".format(rngCnt, rngLen, rng))
		logger.AddTab()
		rngCnt = rngCnt + 1
		for epNum in range(rng[0], rng[1] + 1):
			logger.Print("Episode ({0}/{1}) => {2} ... ".format(epCnt, epLen, epNum))
			logger.AddTab()
			epCnt = epCnt + 1
			isFinished = False
			while not isFinished:
				try:
					downloadUrl = server.grab(epNum)
					dl = Downloader(downloadUrl, getEpisodeName(epNum, fillerList))
					dl.download()
					isFinished = True
				except:
					logger.Print("Error: Error processing episode {0}, Retrying after {1} seconds ...".format(epNum, wait))
					countdown(wait)
			logger.RemoveTab()
		logger.RemoveTab()

if __name__ == "__main__":
	main()

