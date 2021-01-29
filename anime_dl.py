#! /usr/bin/python3

import argparse
import re
import sys

from utils import str2List, logger, countdown

from gogoanime import GoGoAnimeC
from four_anime import FourAnimeC
from animekisa import AnimekisaC
from horriblesubs import HorribleSubsC
from subsplease import SubsPleaseC
from animeultima import AnimeUltimaC

from direct_downloader import DownloaderC
from xdcc_downloader import XDCCDownloaderC

def GetSearchOrder():
	providers = [
		#AnimeUltimaC("", []),
		AnimekisaC("", []),
		FourAnimeC("", []),
		GoGoAnimeC("", []),
		SubsPleaseC("", [])
	]
	cnt = 0
	pLen = len(providers)
	for provider in providers:
		cnt += 1
		logger.Print("{0}) {1}".format(cnt,provider.Name()))
	orderList = input("Search Order [ENTER]: ").strip().split(" ")
	newProviders = []
	for order in orderList:
		try:
			orderNum = int(order) - 1
			if orderNum >= 0 and orderNum < pLen and providers[orderNum] not in newProviders:
				newProviders.append(providers[orderNum])
		except ValueError:
			pass
	for provider in providers:
		if provider not in newProviders:
			newProviders.append(provider)
	logger.Print(" -> ".join([x.Name() for x in newProviders]))
	return newProviders

def search(text):
	providers = GetSearchOrder()
	while True:
		for provider in providers:
			logger.Print("Searching in {0} ...".format(provider.Name()))
			logger.AddTab()
			url = provider.Search(text)
			if url:
				logger.Print("Found Provider: {0}".format(url))
				yield url
			logger.RemoveTab()

def GetServer(url, fillerList):
	isXDCC = False
	server = None
	if "gogoanime" in url:
		server = GoGoAnimeC(url, fillerList)
	elif "horriblesubs" in url:
		server = HorribleSubsC(url, fillerList)
		isXDCC = True
	elif "4anime" in url:
		server = FourAnimeC(url, fillerList)
	elif "animekisa" in url:
		server = AnimekisaC(url, fillerList)
	elif "subsplease" in url:
		server = SubsPleaseC(url, fillerList)
		isXDCC = True
	elif "animeultima" in url:
		server = AnimeUltimaC(url, fillerList)
	else:
		print("Error: URL not supported!", file=sys.stderr)
	return server, isXDCC

def main():
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("-u", "--url"   , help="URL of anime download page"  , dest="url")
	group.add_argument("-s", "--search", help="Search by anime name"        , dest="search")
	parser.add_argument("-l", "--list"  , help="List of episodes, Ex.: 1,3-5", dest="list")
	parser.add_argument("-f", "--filler", help="List of filler episodes"     , dest="fillerList",  default="0")
	parser.add_argument("--skip-filler" , help="Skip downlading fillers"     , dest="skipFiller",  default=False, nargs='?', const=True)
	args = parser.parse_args()

	fillerList = str2List(args.fillerList)
	if(args.search):
		urlGen = search(args.search)
		server, isXDCC = GetServer(next(urlGen), fillerList)
	else:
		urlGen = None
		url = args.url.lower()
		server, isXDCC = GetServer(url, fillerList)
		if not server:
			exit(1)
	if(not args.list):
		args.list = "1-{0}".format(server.EpisodesLen())
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
			if urlGen and not server:
				server, isXDCC = GetServer(next(urlGen), fillerList)
			if args.skipFiller and server.IsFiller(epNum):
				logger.Print("Skipping filler episode.")
			else:
				isFinished = False
				notFoundCnt = 0
				while not isFinished:
					try:
						dlUrl, dlName = server.Grab(epNum)
						if dlUrl:
							logger.Print("URL  => {0}".format(dlUrl))
							logger.Print("Name => {0}".format(dlName))
						else:
							if urlGen:
								notFoundCnt += 1
								if notFoundCnt > 3:
									logger.Print("Not Found, skipping episode!")
									break
								server, isXDCC = GetServer(next(urlGen), fillerList)
								continue
							else:
								logger.Print("Not Found, skipping episode!")
								break
						if isXDCC:
							dl = XDCCDownloaderC(dlUrl, dlName)
						else:
							dl = DownloaderC(dlUrl, dlName)
						isFinished = dl.Download()
						if(not isFinished):
							if urlGen:
								notFoundCnt += 1
								if notFoundCnt > 3:
									logger.Print("Not Found, skipping episode!")
									break
								server, isXDCC = GetServer(next(urlGen), fillerList)
								continue
							else:
								logger.Print("Not Found, skipping episode!")
								break
					except Exception as e:
						logger.Print(e)
						logger.Print("Error: Error processing episode {0}, Retrying after {1} seconds ...".format(epNum, wait))
						countdown(wait)
			logger.RemoveTab()
		logger.RemoveTab()

if __name__ == "__main__":
	main()

