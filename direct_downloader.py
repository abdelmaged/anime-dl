#! /usr/bin/python3

import argparse
import requests
from tqdm import tqdm
from logger import logger
from utils import get_response
import string
import os
import bs4

tbl = dict((ord(char), None) for char in "\\:?/*<>\"|")

class DownloaderC:
	def __init__(self, url, name):
		self.m_url  = url
		self.m_filename = name.translate(tbl)
		self.m_chunk = 1024 
		if 'sbplay' in self.m_url:
				self.m_url = self.__extract_sbplay(self.m_url)


	def Download(self):
		if self.m_url == "":
			return False
		if os.path.isfile(self.m_filename):
			return True
			
		partName = self.m_filename + ".part"
		with open(partName, 'ab') as f:
			headers = {}
			pos = f.tell()
			if pos:
				headers['Range'] = 'bytes={0}-'.format(pos)
			logger.Print("Getting headers ...")
			response = requests.get(self.m_url, headers=headers, stream=True, timeout=60)
			total_size = int(response.headers.get('content-length'))
			if total_size < 512:
				return False
			logger.Print("Getting content ...")
			with tqdm(total=total_size+pos, initial=pos, unit_scale=True, unit='B') as pbar:
				for data in response.iter_content(chunk_size = self.m_chunk):
					f.write(data)
					pbar.update(self.m_chunk)
		os.rename(partName, self.m_filename)
		return True

	def __extract_sbplay(self, url):
			response = get_response(url)
			if response:
					soup = bs4.BeautifulSoup(response.text, 'html.parser')
					table = soup.find('table')
					if table:
							links = table.find_all('a')
							if links:
									code, mode, hash = links[(-1)].get('onclick').replace("'", '').split('(')[(-1)].split(')')[0].split(',')
									url2 = 'https://sbplay.org/dl?op=download_orig&id={0}&mode={1}&hash={2}'.format(code, mode, hash)
									response = get_response(url2)
									if response:
											soup = bs4.BeautifulSoup(response.text, 'html.parser')
											link = soup.find(lambda tag: tag.name == 'a' and 'Direct Download Link' in tag.text)
											if link:
													return link.get('href')
			return url

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--url" , help="URL", dest="url")
	parser.add_argument("-n", "--name", help="Name", dest="name")
	args = parser.parse_args()

	dl = DownloaderC(args.url, args.name)
	dl.Download()

if __name__ == "__main__":
	main()