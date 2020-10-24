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
		self.m_showId, self.m_showTitle = self.__get_show_info()

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			epUrl, epName = self.__get_episode_download_url(pageResponse)
			return epUrl, epName

	def __get_show_info(self):
		urlResponse = self.get_response(self.m_url)
		if(urlResponse):
			soup = bs4.BeautifulSoup(urlResponse.text, 'html.parser')
			links = soup.find_all('script', text=re.compile(r'^var hs_showid'))
			id = ""
			for link in links:
				hsMatch = re.match(r"^var hs_showid = (\d+)", link.text)
				if hsMatch:
					id = hsMatch.group(1)
					break
			title = ""
			heads = soup.find_all('h1')
			for head in heads:
				title = head.getText()
				break
			return id, title
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
			idStr = "{0:02d}-{1}".format(pageResponse.epNum, resolution)
			links = soup.find_all('div', id=idStr)
			for link in links:
				xddLinks = link.find_all('a', text="XDCC")
				epName = self.__get_ep_name(resolution, pageResponse.epNum)
				for xdd in xddLinks:
					xdccLink = xdd.get('href')
					xdccSearch = xdccLink.split('=')[-1]
					xdccResult = self.__get_xdcc_search(xdccSearch, epName)
					if xdccResult:
						return xdccResult, xdccResult['f']
		return None, None

	def __get_xdcc_search(self, text, epNameHint):
		query = {'t': text}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response("https://xdcc.horriblesubs.info/search.php?{0}".format(query))
		if response:
			results = []
			for resMatch in re.findall(r"p\.k\[\d+\] = (.*);", response.text):
				result = js2json(resMatch)
				result = json.loads(result)
				results.append(result)
			if len(results) == 1:
				return results[0]
			else:
				epNameHint = epNameHint.lower()
				for result in results:
					if epNameHint == result['f'].lower():
						return result
				return None

		return None
	
	def __get_ep_name(self, resolution, epNum):
		return "[HorribleSubs] {0} - {1:02d} [{2}].mkv".format(self.m_showTitle, epNum, resolution)
