import bs4
import re
from anime_base import AnimeBaseC
from logger import logger
from urllib.parse import urlencode, quote_plus

class FourAnimeC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)

	def Name(self):
		return "4Anime"

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			epUrl  = self.__get_episode_download_url(pageResponse)
			epName = self.get_episode_name(epNum, epUrl)
			return epUrl, epName
		return "", ""


	def Search(self, text):
		query = {
			's': text
		}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response("https://4anime.to/?{0}".format(query))
		if response:
			soup = bs4.BeautifulSoup(response.text, 'html.parser')
			table = soup.find_all('div', {"id": "headerDIV_2"})
			pages = {}
			for tbl in table:
				links = tbl.find_all('a')
				for link in links:
					href = link.get('href')
					if href and len(href) > 1:
						title = link.find('div')
						if title:
							pages[href] = title.text
			keys, values = list(pages.keys()), list(pages.values())
			if len(keys) == 0:
				return ""
			if len(keys) == 1:
				return keys[0]
			return keys[self.get_user_selection(values) - 1]
		return ""

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
