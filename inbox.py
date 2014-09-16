import znc
import re

class inbox(znc.Module):
	triggers = []
	storageName = "inboxLines"

	def OnLoad(self, args, msg):
		self.triggers.append(self.GetUser().GetNick())
		self.regex = re.compile(self.makeRegex(), flags=re.IGNORECASE)
		self.PutModule("Loaded triggers: %s" % ",".join(self.triggers))
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
		elif command == "debug":
			self.PutModule("%d lines stored" % len(self.lines))
			self.PutModule(repr(self.lines))

		return znc.CONTINUE

	def write(self, lines):
		self.SetNV(self.storageName, "\n".join(lines))

	def read(self):
		stored = self.GetNV(self.storageName)
		return stored.split("\n") if stored != '' else []

	def printout(self, lines):
		if len(lines) == 0:
			self.PutModule("No lines found")
			return
		for line in lines:
			self.PutModule(line)

	def makeRegex(self):
		escaped = map(lambda t: re.escape(t), self.triggers)
		return "(" + "|".join(escaped) + ")"
