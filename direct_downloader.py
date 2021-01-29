#! /usr/bin/python3

import argparse
import requests
from tqdm import tqdm
from logger import logger
import string
import os

tbl = dict((ord(char), None) for char in "\\:?/*<>\"|")

class DownloaderC:
	def __init__(self, url, name):
		self.m_url  = url
		self.m_filename = name.translate(tbl)
		self.m_chunk = 1024 

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

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-u", "--url" , help="URL", dest="url")
	parser.add_argument("-n", "--name", help="Name", dest="name")
	args = parser.parse_args()

	dl = DownloaderC(args.url, args.name)
	dl.Download()

if __name__ == "__main__":
	main()