import bs4
import re
from anime_base import AnimeBaseC
from logger import logger

class AnimekisaC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)

	def Grab(self, epNum):
		logger.Print("Getting URL ... ")
		pageResponse = self.__get_episode_page(epNum)
		if pageResponse:
			epUrl  = self.__get_episode_download_url(pageResponse)
			epName = self.__get_episode_name(epNum, epUrl)
			return epUrl, epName
		return "", ""

	def __get_episode_page(self, epNum):
		response = self.get_response("{0}-episode-{1}".format(self.m_url, epNum))
		if not response:
			response = self.get_response("{0}-episode-{1:02d}".format(self.m_url, epNum))
		return response
	
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
						for link in links:
							dlLink = link.find('a')
							if(dlLink):
								return dlLink.get('href')
		return ""

	def __get_episode_name(self, epNum, epUrl):
		if(self.name):
			return self.name.text
		name = "Episode_{0}".format(epNum)
		if self.IsFiller(epNum):
			name = name + "_filler"
		name = name + ".mp4"
		return name
