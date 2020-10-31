import requests

class AnimeBaseC:
	def __init__(self, url, fillerList):
		self.m_url = url
		self.m_fillerList = fillerList

	def IsFiller(self, epNum):
		for rng in self.m_fillerList:
			if epNum in range(rng[0], rng[1] + 1):
				return True
		return False

	def get_response(self, url):
		response = requests.get(url, timeout=60)
		if response.status_code == 200 and url in response.url:
			return response
		return None

	def __get_episode_name(self, epNum, epUrl):
		if any(tag in epUrl for tag in ["anime1.com", "googleapis", "4animu"]):
			return epUrl.split("?")[0].split("/")[-1]
		name = "Episode_{0}".format(epNum)
		if self.IsFiller(epNum):
			name = name + "_filler"
		name = name + ".mp4"
		return name

	def __get_episode_page(self, epUrl, epNum):
		response = self.get_response("{0}-episode-{1:02d}".format(epUrl, epNum))
		if not response:
			response = self.get_response("{0}-episode-{1}".format(epUrl, epNum))
		if not response:
			response = self.get_response("{0}-episode-{1:02d}-{2:02d}".format(epUrl, epNum, epNum+1))
		if not response:
			response = self.get_response("{0}-episode-{1:02d}-{2:02d}".format(epUrl, epNum-1, epNum))
		return response
