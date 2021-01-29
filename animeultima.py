import bs4
import re
from anime_base import AnimeBaseC
from logger import logger
from urllib.parse import urlencode, quote_plus
import json
import demjson
from utils import js2json

class AnimeUltimaC(AnimeBaseC):
	def __init__(self, url, fillerList):
		super().__init__(url, fillerList)
		self.name = None

	def Name(self):
		return "AnimeUltima"

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
			'search': text
		}
		query = urlencode(query, quote_via=quote_plus)
		response = self.get_response_cloud("https://www1.animeultima.to/search?{0}".format(query))
		if response:
			soup = bs4.BeautifulSoup(response, 'html.parser')
			table = soup.find_all('div', {"class": "column is-one-fifth anime-box"})
			pages = {}
			for tbl in table:
				links = tbl.find_all('a')
				for link in links:
					href = link.get('href')
					if len(href) > 1:
						title = link.get('title')
						if title:
							pages[href] = title
			keys, values = list(pages.keys()), list(pages.values())
			if len(keys) == 0:
				return ""
			if len(keys) == 1:
				self.m_url = keys[0]
			self.m_url = keys[self.get_user_selection(values) - 1]
			self.collect_episodes()
			return self.m_url
		return ""

	def __get_episode_page(self, epNum):
		if epNum < len(self.m_episodes):
			return self.get_response_cloud(self.m_episodes[epNum])
		return super().get_episode_page(self.m_url, epNum, double=False)
	
	def __get_episode_download_url(self, pageResponse):
		if pageResponse:
			html_text = pageResponse
			soup = bs4.BeautifulSoup(html_text, 'html.parser')
			frames = soup.find_all('iframe')
			for frame in frames:
				frame_src = "https://www1.animeultima.to{0}".format(frame.get('src'))
				if(frame_src):
					response = self.get_response_cloud(frame_src)
					if(response):
						frame_soup = bs4.BeautifulSoup(response, 'html.parser')
						scripts = frame_soup.find_all('script')
						for script in scripts:
							setup_params = re.search(r"player\.setup\((.*)\)", script.text, flags=re.DOTALL)
							if(setup_params):
								# text_sub  = re.sub(".*title.*\n?", "", setup_params.group(1))
								# text_sub  = re.sub(".*image.*\n?", "", text_sub)
								# text_sub  = re.sub("'", '"', text_sub)
								jresults = demjson.decode(setup_params.group(1))
								if 'sources' in jresults.keys():
									for source in jresults['sources']:
										print(source)

				# dlLink = re.search(r"var VidStreaming = \"(.*)\"", script.text)
				# if dlLink:
				# 	dlUrl = dlLink.group(1).replace("load.php", "download")
				# 	response = self.get_response(dlUrl)
				# 	if(response):
				# 		html_text = response.text
				# 		soup = bs4.BeautifulSoup(html_text, 'html.parser')
				# 		self.name = soup.find(id="title")
				# 		links = soup.find_all('div', {"class":"dowload"})
				# 		retLink = ""
				# 		for link in links:
				# 			dlLink = link.find('a')
				# 			if dlLink and (retLink == "" or "HDP" in dlLink.text): # 720 link is slow use HDP link instead
				# 				retLink = dlLink.get('href')
				# 		return retLink
		return ""

	def __get_episode_name(self, epNum, epUrl):
		if(self.name):
			return self.name.text + ".mp4"
		return super().get_episode_name(epNum, epUrl)

	def collect_episodes(self):
		response = self.get_response_cloud(self.m_url)
		if response:
			soup = bs4.BeautifulSoup(response, 'html.parser')
			scripts = soup.find_all('script', {"type":"application/ld+json"})
			for script in scripts:
				jresult = json.loads(script.text)
				if 'episodes' in jresult.keys():
					for episode in jresult['episodes']:
						self.m_episodes.append(episode['url'])
