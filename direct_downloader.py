import requests
from tqdm import tqdm
from logger import logger
import string

tbl = dict((ord(char), None) for char in "\\:?/*<>\"|")

class DownloaderC:
	def __init__(self, url, name):
		self.m_url  = url
		self.m_filename = name.translate(tbl)
		self.m_chunk = 1024 

	def Download(self):
		if self.m_url == "":
			return False
		with open(self.m_filename, 'ab') as f:
			headers = {}
			pos = f.tell()
			if pos:
				headers['Range'] = 'bytes={0}-'.format(pos)
			logger.Print("Getting headers ...")
			response = requests.get(self.m_url, headers=headers, stream=True, timeout=60)
			total_size = int(response.headers.get('content-length'))
			logger.Print("Getting content ...")
			with tqdm(total=total_size+pos, initial=pos, unit_scale=True, unit='B') as pbar:
				for data in response.iter_content(chunk_size = self.m_chunk):
					f.write(data)
					pbar.update(self.m_chunk)
		return True
