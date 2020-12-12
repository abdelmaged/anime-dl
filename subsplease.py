import bs4
import re
import json
from anime_base import AnimeBaseC
from logger import logger
from utils import js2json
from urllib.parse import urlencode, quote_plus

class SubsPleaseC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)
		self.m_showId, self.m_showTitle = self.__get_show_info()

	def Name(self):
		return "SubsPlease"

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			epUrl, epName = self.__get_episode_download_url(pageResponse)
			return epUrl, epName

	def Search(self, text):
		query = {
			'f' : 'search', 
			's' : text, 
			'tz': 'eg'
		}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response("https://subsplease.org/api/?{0}".format(query))
		if response and response.text:
			jresult = json.loads(response.text)
			if jresult:
				pages = {}
				for val in jresult.values():
					if 'page' in val:
						pages[val['page']] = val['show']
				keys, values = list(pages.keys()), list(pages.values())
				if len(keys) == 1:
					return "https://subsplease.org/shows/{0}".format(keys[0])
				else:
					return "https://subsplease.org/shows/{0}".format(keys[self.get_user_selection(values) - 1])
		return ""

	def __get_show_info(self):
		urlResponse = self.get_response(self.m_url)
		if(urlResponse):
			soup = bs4.BeautifulSoup(urlResponse.text, 'html.parser')
			id = ""
			showTable = soup.find(id='show-release-table')
			if(showTable):
				id = showTable.get('sid')
			title = ""
			heads = soup.find_all('h1')
			for head in heads:
				title = head.getText()
				break
			return id, title
		return "", ""

	def __get_episode_page(self, epNum):
		query = {
			'f'  : 'show', 
			'sid': self.m_showId, 
			'tz' : 'eg'
		}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response("https://subsplease.org/api/?{0}".format(query))
		if response:
			response.epNum = epNum
		return response
	
	def __get_episode_download_url(self, pageResponse):
		if pageResponse:
			jresult = json.loads(pageResponse.text)
			resolution = "720"
			if self.IsFiller(pageResponse.epNum):
				resolution = "480"
			for val in jresult.values():
				if(val['episode'] == str(pageResponse.epNum)):
					for link in val['downloads']:
						if(link['res'] == resolution):
							epName = self.__get_ep_name(resolution, pageResponse.epNum)
							xdccResult = self.__get_xdcc_search(link['xdcc'], epName)
							if xdccResult:
								return xdccResult, xdccResult['f']
					break
		return None, None

	def __get_xdcc_search(self, text, epNameHint):
		response = self.get_response("https://subsplease.org/xdcc/search.php?t={0}".format(text))
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
					if result['f'].lower().startswith(epNameHint):
						return result
				return None

		return None
	
	def __get_ep_name(self, resolution, epNum):
		return "[SubsPlease] {0} - {1:02d} ({2}p)".format(self.m_showTitle, epNum, resolution)
