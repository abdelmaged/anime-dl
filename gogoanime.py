import bs4
import re
from anime_base import AnimeBaseC
from logger import logger

class GoGoAnimeC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)
		self.m_pageAlt = 1

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			pageUrl =  pageResponse.url
			epUrl   = self.__get_episode_download_url(pageResponse)
			while epUrl == "":
				pageResponse = self.__get_episode_alt_page(pageUrl)
				if not pageResponse:
					break
				epUrl = self.__get_episode_download_url(pageResponse)
		epName = self.__get_episode_name(epNum, epUrl)
		return epUrl, epName

	def __get_episode_page(self, epNum):
		return super().__get_episode_page(self.m_url, epNum)

	def __get_episode_alt_page(self, pageUrl):
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
