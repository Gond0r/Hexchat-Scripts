__module_name__ = "Whois Scanner"
__module_version__ = "0.002"
__module_description__ = "Scan channels for black listed channels in users whois"

import hexchat

Users = []
CurrentUser = ''
CurrentNetwork = ''
GrabbedChans = []

def InitScan(word, word_eol, userdata):
    global Users, CurrentUser, CurrentNetwork, GrabbedChans
    GrabbedChans = []
    CurrentNetwork = hexchat.get_info('network')
    Users = hexchat.get_list("users")
    EventsHook(word, word_eol, userdata)
    CurrentUser = Users[0]
    hexchat.command("whois " + CurrentUser.nick)
    return hexchat.EAT_HEXCHAT

def FnWhoisEnd(word, word_eol, userdata):
    global Users, CurrentUser, CurrentNetwork, GrabbedChans
    network = hexchat.get_info('network')
    nickname = word[0]
    if network == CurrentNetwork and nickname == CurrentUser.nick:
        idx = Users.index(CurrentUser)
        idx += 1
        if idx < len(Users):
            CurrentUser = Users[idx]
            hexchat.command("whois " + CurrentUser.nick)
        else:
            print('finished!')
            EventsUnHook("","","")
            for chan in GrabbedChans:
                print(chan)
        return hexchat.EAT_ALL
    else:
        return hexchat.EAT_NONE

def chanschk(word, word_eol, userdata):
    #print("==data==")
    global Users, CurrentUser, CurrentNetwork, GrabbedChans
    network = hexchat.get_info('network')
    nickname = word[0]
    if network == CurrentNetwork and nickname == CurrentUser.nick:
        #print(word)
        temp = word[1].split()
        for chan in temp:
            channel = chan[chan.find('#'):]
            if channel not in GrabbedChans:
                GrabbedChans.append(channel)
        return hexchat.EAT_ALL
    else:
        return hexchat.EAT_NONE

def EatUseless(word, word_eol, userdata):
    global Users, CurrentUser, CurrentNetwork
    network = hexchat.get_info('network')
    nickname = word[0]
    if network == CurrentNetwork and nickname == CurrentUser.nick:
        return hexchat.EAT_ALL
    else:
        return hexchat.EAT_NONE

def ShowProg(word, word_eol, userdata):
    global CurrentUser, Users
    print('whoising',CurrentUser.nick,'no.',Users.index(CurrentUser),'of',len(Users),'(',len(Users) - Users.index(CurrentUser) -1,'to go)')
    return hexchat.EAT_NONE
    
def LoopAbort(word, word_eol, userdata):
    global CurrentNetwork
    network = hexchat.get_info('network')
    if network == CurrentNetwork:
        EventsUnHook("","","")
    return hexchat.EAT_NONE

def EventsHook(word, word_eol, userdata):
    hexchat.hook_print("WhoIs End", FnWhoisEnd)
    hexchat.hook_print("WhoIs Channel/Oper Line", chanschk)
    hexchat.hook_print("WhoIs Identified", EatUseless)
    hexchat.hook_print("WhoIs idle Line", EatUseless)
    hexchat.hook_print("WhoIs idle Line With Signon", EatUseless)
    hexchat.hook_print("WhoIs Name Line", EatUseless)
    hexchat.hook_print("WhoIs Real Host", EatUseless)
    hexchat.hook_print("WhoIs Server Line", EatUseless)
    hexchat.hook_print("WhoIs Special", EatUseless)
    hexchat.hook_print("WhoIs Authenticated", EatUseless)
    hexchat.hook_print("WhoIs Away Line", EatUseless)
    return hexchat.EAT_NONE

def EventsUnHook(word, word_eol, userdata):
    hexchat.unhook("WhoIs End")
    hexchat.unhook("WhoIs Channel/Oper Line")
    hexchat.unhook("WhoIs Identified")
    hexchat.unhook("WhoIs idle Line")
    hexchat.unhook("WhoIs idle Line With Signon")
    hexchat.unhook("WhoIs Name Line")
    hexchat.unhook("WhoIs Real Host")
    hexchat.unhook("WhoIs Server Line")
    hexchat.unhook("WhoIs Special")
    hexchat.unhook("WhoIs Authenticated")
    hexchat.unhook("WhoIs Away Line")
    return hexchat.EAT_NONE

def unload_callback(userdata):
    print("\0034" + __module_name__ + '\tVersion ' + __module_version__ + ' unloaded.\003')

hexchat.hook_unload(unload_callback)
hexchat.hook_command("SCAN", InitScan)
hexchat.hook_command("SCANPROG", ShowProg)
hexchat.hook_command("SCANABORT", LoopAbort)
hexchat.hook_command("TAKE", EventsHook)
hexchat.hook_command("UNTAKE", EventsUnHook)
print("\0034" + __module_name__ + '\tVersion ' + __module_version__ + ' loaded.\003')
