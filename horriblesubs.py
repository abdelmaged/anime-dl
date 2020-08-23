import bs4
import re
import json
from anime_base import AnimeBaseC
from logger import logger
from utils import js2json
from urllib.parse import urlencode, quote_plus

class HorribleSubsC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)
		self.m_showId = self.__get_show_id()

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			epUrl, epName = self.__get_episode_download_url(pageResponse)
			return epUrl, epName

	def __get_show_id(self):
		urlResponse = self.get_response(self.m_url)
		if(urlResponse):
			soup = bs4.BeautifulSoup(urlResponse.text, 'html.parser')
			links = soup.find_all('script', text=re.compile(r'^var hs_showid'))
			for link in links:
				hsMatch = re.match(r"^var hs_showid = (\d+)", link.text)
				if hsMatch:
					return hsMatch.group(1)
		return ""

	def __get_episode_page(self, epNum):
		query = {
			'method': 'getshows', 
			'type'  : 'show', 
			'showid': self.m_showId, 
			'mode'  : 'filter', 
			'value' : epNum
		}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response("https://horriblesubs.info/api.php?{0}".format(query))
		if response:
			response.epNum = epNum
		return response
	
	def __get_episode_download_url(self, pageResponse):
		if pageResponse:
			html_text = pageResponse.text
			soup = bs4.BeautifulSoup(html_text, 'html.parser')
			resolution = "720p"
			if self.IsFiller(pageResponse.epNum):
				resolution = "480p"
			idStr = "{0}-{1}".format(pageResponse.epNum, resolution)
			link = soup.find('div', {"id": idStr})
			if link:
				xddLinks = link.find_all('a', text="XDCC")
				for xdd in xddLinks:
					xdccLink = xdd.get('href')
					xdccSearch = xdccLink.split('=')[-1]
					xdccResult = self.__get_xdcc_search(xdccSearch)
					return xdccResult, xdccResult['f']
		return None, None

	def __get_xdcc_search(self, text):
		query = {'t': text}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response("https://xdcc.horriblesubs.info/search.php?{0}".format(query))
		if response:
			resMatch = re.match(r"p\.k\[0\] = (.*);", response.text)
			if resMatch:
				result = resMatch.group(1)
				result = js2json(result)
				result = json.loads(result)
				return result
		return None
