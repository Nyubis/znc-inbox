import znc
import re

class inbox(znc.Module):
	triggers = []

	def OnLoad(self, args, msg):
		self.triggers.append(self.GetUser().GetNick())
		self.regex = re.compile(makeRegex(), flags=re.IGNORECASE)
		self.PutModule("Loaded triggers: %s" % ",".join(self.triggers))
		
		return znc.CONTINUE

	def OnChanMsg(self, nick, channel, msg):
		if self.regex.search(str(msg.s)) != None:
			self.PutModule("<%s> %s" % (nick, msg.s))

		return znc.CONTINUE

	def makeRegex(self):
		escaped = map(lambda t: re.escape(t), self.triggers)
		return "(" + "|".join(escaped) + ")"
