#! /usr/bin/python3

import argparse
import re
import sys
from utils import str2List, logger, countdown
from gogoanime import GoGoAnimeC
from four_anime import FourAnimeC
from animekisa import AnimekisaC
from horriblesubs import HorribleSubsC
from direct_downloader import DownloaderC
from xdcc_downloader import XDCCDownloaderC



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--url"   , help="URL of anime download page"  , dest="url"       ,  required=True)    
	parser.add_argument("-l", "--list"  , help="List of episodes, Ex.: 1,3-5", dest="list"      ,  default="1-999")
	parser.add_argument("-f", "--filler", help="List of filler episodes"     , dest="fillerList",  default="0")
	parser.add_argument("--skip-filler" , help="Skip downlading fillers"     , dest="skipFiller",  default=False, nargs='?', const=True)
	args = parser.parse_args()

	isXDCC = False	
	url = args.url.lower()
	fillerList = str2List(args.fillerList)
	if "gogoanime" in url:
		server = GoGoAnimeC(args.url, fillerList)
	elif "horriblesubs" in url:
		server = HorribleSubsC(args.url, fillerList)
		isXDCC = True
	elif "4anime" in url:
		server = FourAnimeC(args.url, fillerList)
	elif "animekisa" in url:
		server = AnimekisaC(args.url, fillerList)
	else:
		print("Error: URL not supported! Supported: GoGoAnime", file=sys.stderr)
		return

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
						if dlUrl:
							logger.Print("URL  => {0}".format(dlUrl))
							logger.Print("Name => {0}".format(dlName))
						else:
							logger.Print("Not Found, skipping episode!")
							break
						if isXDCC:
							dl = XDCCDownloaderC(dlUrl, dlName)
						else:
							dl = DownloaderC(dlUrl, dlName)
						isFinished = dl.Download()
						if(not isFinished):
							logger.Print("Error: Error processing episode {0}, Retrying after {1} seconds ...".format(epNum, wait))
							countdown(wait)	
					except Exception as e:
						logger.Print(e)
						logger.Print("Error: Error processing episode {0}, Retrying after {1} seconds ...".format(epNum, wait))
						countdown(wait)
			logger.RemoveTab()
		logger.RemoveTab()

if __name__ == "__main__":
	main()

