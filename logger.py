import sys

class LoggerC:
	def __init__(self, file=sys.stdout):
		self.m_tab  = 0
		self.m_file = file 
	
	def AddTab(self):
		self.m_tab = self.m_tab + 1

	def RemoveTab(self):
		if self.m_tab > 0:
			self.m_tab = self.m_tab - 1

	def Print(self, msg, end='\n', tab=True):
		if tab:
			self.__printTabs()
		print(msg, file=self.m_file, end=end)

	def __printTabs(self):
		for _ in range(0, self.m_tab):
			print("  ", end='', file=self.m_file)

logger = LoggerC()
