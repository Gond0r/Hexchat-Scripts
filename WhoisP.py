__module_name__ = "WhoisScanner"
__module_version__ = "0.001"
__module_description__ = "Whois Scanner"

print "\0034",__module_name__, __module_version__,"has been loaded\003"

import hexchat

Users = []
CurrentUser = 0
UsersCount = 0

def InitScan(word, word_eol, userdata):
	GetData()
	EventsHook(word, word_eol, userdata)
	StartLoop()
	return hexchat.EAT_HEXCHAT

def GetData():
	global Users, UsersCount, CurrentUser
	Users = hexchat.get_list("users")
	UsersCount = len(Users)
	UsersCount = UsersCount - 1
	return

def StartLoop():
	global Users, UsersCount, CurrentUser
	CurrentUser = 0
	DoWhois()
	return

def FnWhoisEnd(word, word_eol, userdata):
	global Users, UsersCount, CurrentUser
	#print("whois endded")
	StepLoop()
	return hexchat.EAT_ALL

def StepLoop():
	global Users, UsersCount, CurrentUser
	CurrentUser = CurrentUser + 1
	#print("now ", CurrentUser)
	if ( CurrentUser > UsersCount ):
		print("terminating")
		CurrentUser = 0
		UsersCount = 0
		EventsUnHook("","","")
		#print("done")
		return
	else:
		#print(CurrentUser, " ",Users[CurrentUser].nick)
		DoWhois()
		return hexchat.EAT_NONE

def DoWhois():
	global Users, UsersCount, CurrentUser
	hexchat.command("whois " + Users[CurrentUser].nick)
	return

def chanschk(word, word_eol, userdata):
	#print("==data==")
	print(word_eol[0])
	return hexchat.EAT_ALL

def EatUseless(word, word_eol, userdata):
	return hexchat.EAT_ALL

def ShowProg(word, word_eol, userdata):
	global UsersCount, CurrentUser
	print(CurrentUser)
	return hexchat.EAT_NONE
	
def LoopAbort(word, word_eol, userdata):
	global UsersCount, CurrentUser
	CurrentUser = UsersCount
	EventsUnHook("","","")
	return hexchat.EAT_NONE

def EventsHook(word, word_eol, userdata):
	hexchat.hook_print("WhoIs End", FnWhoisEnd)
	hexchat.hook_print("WhoIs Channel/Oper Line", chanschk)
	hexchat.hook_print("Whois Identified", EatUseless)
	hexchat.hook_print("Whois idle Line", EatUseless)
	hexchat.hook_print("Whois idle Line With Signon", EatUseless)
	hexchat.hook_print("Whois Name Line", EatUseless)
	hexchat.hook_print("Whois Real Host", EatUseless)
	hexchat.hook_print("Whois Server Line", EatUseless)
	hexchat.hook_print("Whois Special", EatUseless)
	hexchat.hook_print("Whois Authenticated", EatUseless)
	hexchat.hook_print("Whois Away Line", EatUseless)
	return hexchat.EAT_NONE

def EventsUnHook(word, word_eol, userdata):
	hexchat.unhook("WhoIs End")
	hexchat.unhook("WhoIs Channel/Oper Line")
	hexchat.unhook("Whois Identified")
	hexchat.unhook("Whois idle Line")
	hexchat.unhook("Whois idle Line With Signon")
	hexchat.unhook("Whois Name Line")
	hexchat.unhook("Whois Real Host")
	hexchat.unhook("Whois Server Line")
	hexchat.unhook("Whois Special")
	hexchat.unhook("Whois Authenticated")
	hexchat.unhook("Whois Away Line")
	return hexchat.EAT_NONE

hexchat.hook_command("SCAN", InitScan)
hexchat.hook_command("SCANPROG", ShowProg)
hexchat.hook_command("SCANABORT", LoopAbort)
hexchat.hook_command("TAKE", EventsHook)
hexchat.hook_command("UNTAKE", EventsUnHook)
