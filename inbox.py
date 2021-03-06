import znc
import re
from datetime import datetime

class inbox(znc.Module):
	triggers = set() 
	lineStorage = "inboxLines"
	triggerStorage = "inboxTriggers"

	def OnLoad(self, args, msg):
		self.readTriggers()
		self.addTrigger(self.GetUser().GetNick(), printout=False)
		self.lines = self.read()
		self.missedLineCount = 0
		self.short_regex = re.compile("\<.*$")
		self.commands = {
			'show': self.com_show,
			'show-v': self.com_showVerbose,
			'add-trigger': self.com_addTrigger,
			'remove-trigger': self.com_rmTrigger,
			'debug': self.com_debug
		}
		
		return znc.CONTINUE

	def OnChanMsg(self, nick, channel, msg):
		if self.regex.search(str(msg.s)) != None:
			timestamp = datetime.now().strftime("%d/%m %H:%M")
			self.lines.append("%s [%s] <%s> %s" % (channel, timestamp, nick, msg.s))
			self.write(self.lines)
			if not self.connected:
				self.missedLineCount += 1

		return znc.CONTINUE

	def OnModCommand(self, command):
		words = command.split(' ')
		keyword = words[0]
		if keyword in self.commands:
			self.commands[keyword](words[1:])
		else:
			self.PutModule("Unknown command. Known commands are %s" %
					", ".join(self.commands.keys()))

		return znc.CONTINUE

	def OnClientLogin(self):
		self.connected = True
		if self.missedLineCount == 0:
			return znc.CONTINUE

		missedLines = self.lines[-self.missedLineCount:]
		for line in missedLines:
			self.PutModule(line)
		self.missedLineCount = 0

		return znc.CONTINUE

	def OnClientDisconnect(self):
		self.connected = False

		return znc.CONTINUE

	def com_show(self, params, verbose=False):
		if len(params) == 0:
			self.PutModule("Specify how many lines you want to see, e.g.: show 5")
			return
		try:
			count = int(params[0])
			if verbose:
				self.printout(self.lines[-count:])
			else:
				l = lambda x: self.short_regex.search(x).group()
				self.printout(list(map(l, self.lines[-count:])))
		except ValueError:
			self.PutModule("Invalid syntax. %s does not appear to be a number" % params[0])

	def com_showVerbose(self, params):
		self.com_show(params, verbose=True)

	def com_debug(self, params):
		self.PutModule("triggers: %s" % repr(triggers))
		self.PutModule("%d lines stored" % len(self.lines))
		self.PutModule(repr(self.lines))
		
	def com_addTrigger(self, params):
		if len(params) > 0 and len(params[0]) > 0:
			self.addTrigger(params[0])
		else:
			self.PutModule("Can't add an empty trigger")

	def com_rmTrigger(self, params):
		if len(params) > 0 and len(params[0]) > 0:
			if params[0] in self.triggers:
				self.triggers.remove(params[0])
				self.writeTriggers(self.triggers)
				self.PutModule("Current triggers: %s" % ", ".join(self.triggers))
			else:
				self.PutModule("No such trigger")
		else:
			self.PutModule("Can't remove an empty trigger")


	def write(self, lines):
		self.SetNV(self.lineStorage, "\n".join(lines))

	def read(self):
		stored = self.GetNV(self.lineStorage)
		return stored.split("\n") if stored != '' else []

	def printout(self, lines):
		if len(lines) == 0:
			self.PutModule("No lines found")
			return
		for line in lines:
			self.PutModule(line)

	def addTrigger(self, trigger, printout=True):
		self.triggers.add(trigger)
		self.regex = re.compile(self.makeRegex(), flags=re.IGNORECASE)
		self.writeTriggers(self.triggers)
		if printout:
			self.PutModule("Current triggers: %s" % ", ".join(self.triggers))

	def writeTriggers(self, triggers):
		self.SetNV(self.triggerStorage, '\n'.join(triggers))

	def readTriggers(self):
		stored = self.GetNV(self.triggerStorage)
		if len(stored) > 0:
			triggers = stored.split('\n')
			for trigger in triggers:
				self.addTrigger(trigger, printout=False)

	def makeRegex(self):
		escaped = map(lambda t: re.escape(t), self.triggers)
		return "(" + "|".join(escaped) + ")"
