import znc
import re

class inbox(znc.Module):
	triggers = set() 
	lineStorage = "inboxLines"
	triggerStorage = "inboxTriggers"

	def OnLoad(self, args, msg):
		self.readTriggers()
		self.addTrigger(self.GetUser().GetNick())
		self.lines = self.read()
		
		return znc.CONTINUE

	def OnChanMsg(self, nick, channel, msg):
		if self.regex.search(str(msg.s)) != None:
			self.lines.append("<%s> %s" % (nick, msg.s))
			self.write(self.lines)

		return znc.CONTINUE

	def OnModCommand(self, command):
		if command[:5] == "show ":
			try:
				count = int(command[5:])
				self.printout(self.lines[-count:])
			except ValueError:
				self.PutModule("Invalid syntax. %s does not appear to be a number" % command[5:])
		elif command[:12] == "add trigger ":
			trigger = command[12:]
			if len(trigger) > 0:
				self.addTrigger(trigger)
			else:
				self.PutModule("Can't add an empty trigger")
		elif command == "debug":
			self.PutModule("%d lines stored" % len(self.lines))
			self.PutModule(repr(self.lines))

		return znc.CONTINUE

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

	def addTrigger(self, trigger):
		self.triggers.add(trigger)
		self.regex = re.compile(self.makeRegex(), flags=re.IGNORECASE)
		self.writeTriggers(self.triggers)
		self.PutModule("Current triggers: %s" % ", ".join(self.triggers))

	def writeTriggers(self, triggers):
		self.SetNV(self.triggerStorage, '\n'.join(triggers))

	def readTriggers(self):
		stored = self.GetNV(self.triggerStorage)
		if len(stored) > 0:
			triggers = stored.split('\n')
			for trigger in triggers:
				self.addTrigger(trigger)

	def makeRegex(self):
		escaped = map(lambda t: re.escape(t), self.triggers)
		return "(" + "|".join(escaped) + ")"
