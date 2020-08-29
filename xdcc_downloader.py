import subprocess
import os

class XDCCDownloaderC:
	def __init__(self, xdcc, name):
		self.m_xdcc = xdcc
		self.m_filename = name

	def Download(self):
		if not self.m_xdcc:
			return False
		dlPath = os.getcwd()
		# shellCommand = [
		# 	'xterm', 
		# 	'-e'
		# ]
		command = [
			'weechat', 
			'-r', 
			# '"'
		]
		weechatCommands = [
			'/set xfer.file.auto_accept_files on',
			'/set xfer.file.use_nick_in_filename off',
			'/set xfer.file.convert_spaces off',
			'/set xfer.file.download_path {0}'.format(dlPath),
			'/server add AnimeDLRizon irc.rizon.net',
			'/set irc.server.AnimeDLRizon.autojoin #horriblesubs'
		]
		onJoinCommands = [
			"/set irc.server.AnimeDLRizon.command '/msg {0} xdcc send #{1}".format(self.m_xdcc['b'], self.m_xdcc['n']),
			'/wait 3s /buffer 3',
			'/trigger addreplace anime_dl_xfer_ended_hook signal xfer_ended \\"\\" \\"\\" \\"/quit\\"\''
		]
		weechatCommands.append('\;'.join(onJoinCommands))
		weechatCommands.append('/connect AnimeDLRizon')
		command.append(';'.join(weechatCommands))
		# command.append('"')
		# shellCommand.append(' '.join(command))
		subprocess.run(command)
		return os.path.isfile(self.m_xdcc['f'])
