import bs4
import re
from anime_base import AnimeBaseC
from logger import logger
from urllib.parse import urlencode, quote_plus

class AnimekisaC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)
		self.name = None

	def Name(self):
		return "AnimeKisa"

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			epUrl  = self.__get_episode_download_url(pageResponse)
			epName = self.__get_episode_name(epNum, epUrl)
			return epUrl, epName
		return "", ""

	def Search(self, text):
		query = {
			'q': text
		}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response("https://animekisa.tv/search?{0}".format(query))
		if response:
			soup = bs4.BeautifulSoup(response.text, 'html.parser')
			table = soup.find_all('div', {"class": "lisbg"})
			for tbl in table:
				if tbl.text == "Subbed":
					mainbox = tbl.find_next_sibling()
					if mainbox:
						links = mainbox.find_all('a')
						pages = {}
						for link in links:
							href = link.get('href')
							if len(href) > 1:
								title = link.find('div', {"class": "similardd"})
								if title:
									pages[href] = title.text
						keys, values = list(pages.keys()), list(pages.values())
						if len(keys) == 0:
							return ""
						if len(keys) == 1:
							return "https://animekisa.tv{0}".format(keys[0])
						return "https://animekisa.tv{0}".format(keys[self.get_user_selection(values) - 1])
					break
		return ""

	def __get_episode_page(self, epNum):
		if epNum < len(self.m_episodes):
			return self.get_response(self.m_episodes[-epNum])
		return super().get_episode_page(self.m_url, epNum, double=False)
	
	def __get_episode_download_url(self, pageResponse):
		if pageResponse:
			html_text = pageResponse.text
			soup = bs4.BeautifulSoup(html_text, 'html.parser')
			scripts = soup.find_all('script')
			for script in scripts:
				dlLink = re.search(r"var VidStreaming = \"(.*)\"", script.text)
				if dlLink:
					dlUrl = dlLink.group(1).replace("load.php", "download")
					response = self.get_response(dlUrl)
					if(response):
						html_text = response.text
						soup = bs4.BeautifulSoup(html_text, 'html.parser')
						self.name = soup.find(id="title")
						links = soup.find_all('div', {"class":"dowload"})
						retLink = ""
						for link in links:
							dlLink = link.find('a')
							if dlLink and (retLink == "" or "HDP" in dlLink.text): # 720 link is slow use HDP link instead
								retLink = dlLink.get('href')
						return retLink
		return ""

	def __get_episode_name(self, epNum, epUrl):
		if(self.name):
			return self.name.text + ".mp4"
		return super().get_episode_name(epNum, epUrl)

	def collect_episodes(self):
		response = self.get_response(self.m_url)
		if response:
			soup = bs4.BeautifulSoup(response.text, 'html.parser')
			links = soup.find_all('a', {"class":"infovan"})
			for link in links:
				self.m_episodes.append("https://animekisa.tv/" + link.get('href'))

