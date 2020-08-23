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
