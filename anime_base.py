import requests
from logger import logger
from utils import similar
import json

class AnimeBaseC:
	def __init__(self, url, fillerList):
		self.m_url = url
		self.m_fillerList = fillerList
		self.m_episodes = []
		self.collect_episodes()
		self.session = None

	def IsFiller(self, epNum):
		for rng in self.m_fillerList:
			if epNum in range(rng[0], rng[1] + 1):
				return True
		return False

	def Search(self, text):
		return ""
	
	def get_response(self, url):
		if url:
			response = requests.get(url, timeout=60)
			if response.status_code == 200 and similar(url, response.url) > 0.80:
				return response
		return None

	def get_response_cloud(self, url):
		# if not self.session:
		# 	headers = {
		# 		'Content-Type': 'application/json',
		# 	}
		# 	data = { 
		# 		"cmd": "sessions.create",
		# 		"session": "my_cloud_1",
		# 		"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW...", 
		# 	}
			
		# 	response = requests.post('http://localhost:8191/v1', headers=headers, data=json.dumps(data))
		# 	self.session = "my_cloud_1"

		if url:
			headers = {
				'Content-Type': 'application/json',
			}
			data = { 
				"cmd": "request.get", 
				"url": url, 
				"session": "my_cloud_1",
				"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW...", 
				"maxTimeout": 60000, 
				"headers": { 
					"X-Test": "Testing 123..."
				}
			}
			
			response = requests.post('http://localhost:8191/v1', headers=headers, data=json.dumps(data))
			if response.status_code == 200:
				response = json.loads(response.text)
				return response['solution']['response']
		return None
		
	def get_episode_name(self, epNum, epUrl):
		if any(tag in epUrl for tag in ["anime1.com", "googleapis", "4animu"]):
			return epUrl.split("?")[0].split("/")[-1]
		name = "Episode_{0}".format(epNum)
		if self.IsFiller(epNum):
			name = name + "_filler"
		name = name + ".mp4"
		return name

	def get_episode_page(self, epUrl, epNum, double=True):
		response = self.get_response("{0}-episode-{1:02d}".format(epUrl, epNum))
		if not response:
			response = self.get_response("{0}-episode-{1}".format(epUrl, epNum))
		if double:
			if not response:
				response = self.get_response("{0}-episode-{1:02d}-{2:02d}".format(epUrl, epNum, epNum+1))
			if not response:
				response = self.get_response("{0}-episode-{1}-{2}".format(epUrl, epNum, epNum+1))
			if not response:
				response = self.get_response("{0}-episode-{1:02d}-{2:02d}".format(epUrl, epNum-1, epNum))
			if not response:
				response = self.get_response("{0}-episode-{1}-{2}".format(epUrl, epNum-1, epNum))
		return response

	def get_user_selection(self, animeSet):
		cnt = 0
		for name in animeSet:
			if cnt > 4:
				break
			cnt += 1
			logger.Print("{0}) {1}".format(cnt, name))
		while True:
			try:
				sel = int(input("Select: "))
				if sel < 1 or sel > cnt:
					raise ValueError
				return sel
			except ValueError:
				logger.Print("Invalid selection.")

	def collect_episodes(self):
		return

	def EpisodesLen(self):
		epLen = len(self.m_episodes) 
		if epLen > 0:
			return epLen
		return 999