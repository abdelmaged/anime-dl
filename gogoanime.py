import bs4
import re
from anime_base import AnimeBaseC
from logger import logger
from urllib.parse import urlencode, quote_plus
import json

class GoGoAnimeC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)
		self.m_pageAlt = 1

	def Name(self):
		return "GoGoAnime"

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		epUrl = ""
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			pageUrl =  pageResponse.url
			epUrl   = self.__get_episode_download_url(pageResponse)
			while epUrl == "":
				pageResponse = self.__get_episode_alt_page(pageUrl)
				if not pageResponse:
					break
				epUrl = self.__get_episode_download_url(pageResponse)
		epName = self.get_episode_name(epNum, epUrl)
		return epUrl, epName

	def Search(self, text):
		query = {
			'q': text
		}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response("https://www.gogoanime1.com/search/topSearch?{0}".format(query))
		if response:
			jresult = json.loads(response.text)
			if jresult and jresult['data']:
				keys = []
				values = []
				for val in jresult['data']:
					keys.append(val['seo_name'])
					values.append(val['name'])
				if len(keys) == 1:
					return "https://www.gogoanime1.com/watch/{0}".format(keys[0])
				else:
					user_sel = self.get_user_selection(values)
					if user_sel == -1:
							return ''
					return 'https://www.gogoanime1.com/watch/{0}'.format(keys[(user_sel - 1)])
		return ""

	def __get_episode_page(self, epNum):
		response = self.get_response("{0}/episode/episode-{1}".format(self.m_url, epNum))
		if not response:
			response = self.get_response("{0}/episode/episode-{1}-{2}".format(self.m_url, epNum, epNum+1))
		if not response:
			response = self.get_response("{0}/episode/episode-{1}-{2}".format(self.m_url, epNum-1, epNum))
		return response

	def __get_episode_alt_page(self, pageUrl):
		if self.m_pageAlt > 3:
			return None
		response = self.get_response("{0}/{1}".format(pageUrl, self.m_pageAlt))
		self.m_pageAlt = self.m_pageAlt + 1
		return response
	
	def __get_episode_download_url(self, pageResponse):
		if pageResponse:
			html_text = pageResponse.text
			soup = bs4.BeautifulSoup(html_text, 'html.parser')
			links = soup.find_all('a', text=re.compile(r'^Download$'))
			for link in links:
				return link.get('href')
		return ""

	def __get_episode_page(self, epNum):
		if epNum <= len(self.m_episodes):
			return self.get_response(self.m_episodes[-epNum])
		return super().get_episode_page(self.m_url, epNum)

	def collect_episodes(self):
		response = self.get_response(self.m_url)
		if response:
			soup = bs4.BeautifulSoup(response.text, 'html.parser')
			uls = soup.find_all('ul', {"class":"check-list"})
			uls_len = len(uls)
			if uls_len > 0:
				if uls_len > 1:
					ul_index = 1
				else:
					ul_index = 0
				links = uls[ul_index].find_all('a')
				for link in links:
					self.m_episodes.append(link.get('href'))
