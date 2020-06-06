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

class LoggerC:
	def __init__(self, file=sys.stdout):
		self.m_tab  = 0
		self.m_file = file 
	
	def AddTab(self):
		self.m_tab = self.m_tab + 1

	def RemoveTab(self):
		if self.m_tab > 0:
			self.m_tab = self.m_tab - 1

	def Print(self, msg, end='\n', tab=True):
		if tab:
			self.__printTabs()
		print(msg, file=self.m_file, end=end)

	def __printTabs(self):
		for i in range(0, self.m_tab):
			print("  ", end='', file=self.m_file)

class DownloaderC:
	def __init__(self, url, name):
		self.m_url  = url
		self.m_filename = name
		self.m_chunk = 1024 

	def Download(self):
		if self.m_url == "":
			return False
		with open(self.m_filename, 'ab') as f:
			headers = {}
			pos = f.tell()
			if pos:
				headers['Range'] = 'bytes={0}-'.format(pos)
			logger.Print("Getting headers ...")
			response = requests.get(self.m_url, headers=headers, stream=True, timeout=60)
			total_size = int(response.headers.get('content-length'))
			logger.Print("Getting content ...")
			with tqdm(total=total_size+pos, initial=pos, unit_scale=True, unit='B') as pbar:
				for data in response.iter_content(chunk_size = self.m_chunk):
					f.write(data)
					pbar.update(self.m_chunk)
		return True

class GoGoAnimeC:
	def __init__(self, url, fillerList):
		self.m_url = url
		self.m_fillerList = fillerList

	def Grab(self, epNum):
		epUrl = "{0}/episode/episode-{1}".format(self.m_url, epNum)
		logger.Print("Getting URL ... ")
		epUrl = self.__get_episode_download_url(epUrl)
		if epUrl == "":
			epUrl = "{0}/episode/episode-{1}-{2}".format(self.m_url, epNum, epNum+1)
			epUrl = self.__get_episode_download_url(epUrl)
		epName = self.__get_episode_name(epNum, epUrl)
		logger.Print("URL => {0}, Name => {1}".format(epUrl, epName))
		return epUrl, epName

	def IsFiller(self, epNum):
		for rng in self.m_fillerList:
			if epNum in range(rng[0], rng[1] + 1):
				return True
		return False

	def __get_episode_download_url(self, epUrl):
		html_text = requests.get(epUrl).text
		soup = bs4.BeautifulSoup(html_text, 'html.parser')
		links = soup.find_all('a', text=re.compile(r'^Download$'))
		for link in links:
			return link.get('href')
		return ""

	def __get_episode_name(self, epNum, epUrl):
		if "anime1.com" in epUrl:
			return epUrl.split("?")[0].split("/")[-1]
		name = "Episode_{0}".format(epNum)
		if self.IsFiller(epNum):
			name = name + "_filler"
		name = name + ".mp4"
		return name

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--url"   , help="URL of anime download page"  , dest="url"       ,  required=True)    
	parser.add_argument("-l", "--list"  , help="List of episodes, Ex.: 1,3-5", dest="list"      ,  default="1-999")
	parser.add_argument("-f", "--filler", help="List of filler episodes"     , dest="fillerList",  default="0")
	parser.add_argument("--skip-filler" , help="Skip downlading fillers"     , dest="skipFiller",  default=False, nargs='?', const=True)
	args = parser.parse_args()
	
	url = args.url.lower()
	fillerList = str2List(args.fillerList)
	if "gogoanime" in url:
		server = GoGoAnimeC(args.url, fillerList)
	else:
		print("Error: URL not supported! Supported: GoGoAnime", file=sys.stderr)
		return

	global logger
	logger = LoggerC()
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
			if args.skipFiller and server.IsFiller(epNum):
				logger.Print("Skipping filler episode.")
			else:
				isFinished = False
				while not isFinished:
					try:
						dlUrl, dlName = server.Grab(epNum)
						dl = DownloaderC(dlUrl, dlName)
						dl.Download()
						isFinished = True
					except:
						logger.Print("Error: Error processing episode {0}, Retrying after {1} seconds ...".format(epNum, wait))
						countdown(wait)
			logger.RemoveTab()
		logger.RemoveTab()

if __name__ == "__main__":
	main()

