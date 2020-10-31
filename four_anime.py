import bs4
import re
from anime_base import AnimeBaseC
from logger import logger

class FourAnimeC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			epUrl  = self.__get_episode_download_url(pageResponse)
			epName = self.get_episode_name(epNum, epUrl)
			return epUrl, epName
		return "", ""

	def __get_episode_page(self, epNum):
		url = self.m_url.replace("/anime/", "/")
		return super().get_episode_page(url, epNum)
	
	def __get_episode_download_url(self, pageResponse):
		if pageResponse:
			html_text = pageResponse.text
			soup = bs4.BeautifulSoup(html_text, 'html.parser')
			scripts = soup.find_all('script', {"type":"text/javascript"})
			for script in scripts:
				if "mirror_dl" in script.text:
					return script.text.split('"')[3].replace('\\', '')
		return ""
