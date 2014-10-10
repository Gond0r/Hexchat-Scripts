__module_name__ = "Users Away Notifier"
__module_version__ = "0.002"
__module_description__ = "Get notified in the active window when users set away or set back."
# Todos:
# 1. add a setting for notification color

import hexchat

AllUsers = {}
AllChannels = {}
ScanProgress = {}
def unload_callback(userdata):
    print("\0034" + __module_name__ + '\tVersion ' + __module_version__ + ' unloaded.\003')

# Format: 352 <channel> <username> <address> <server> <nick> <flags> :<hops> <info>
# <channel> A channel the user is on, or * for none visible.
# <username> The username (identd) of the user.
# <address> The IP or resolved address (host) of the user.
# <server> The server the user is connected to.
# <nick> The nickname of the user.
# <flags> Flags for a user regarding IRCop status, away status, channel op status, etc.
# <hops> The number of hops from your server the the user's server.
# <info> The user's "real name" info.
# Info: This is returned by a WHO request, one line for each user that is matched.
# Notes: If the user is on multiple channels, only one will be returned. If the WHO was performed on a channel, this will always be the channel that was requested.
# Private and secret channels are not returned unless you are on them as well.
# The flags will always start with H (here) if the user is not away, or G (gone) if the user is away.
# This is followed by a * (asterisk) if the user is an IRCop, then a @ or + if the user is opped or voiced on the listed channel.
# This is then followed by a d (lowercase) if the user is deaf, such as X and W on Undernet.
# The hop count ('hops') is a count of the number of servers between your server and their server. If they are on your server, this will be 0.
# If they are on a server directly connected to your server, this is 1. If there is one intervening server, this is 2, etc.
# The info (real name) is provided by the user on signon and may contain anything.
# WHO hexchat.hook_server("315", WhoEnd)
def WhoRPL(word,word_eol,userdata):
    global AllUsers
    network = hexchat.get_info('network')
    if word[3].find('#') != -1 or word[3].find('*') != -1:
        nickname_idx = 7
        nickname_flag_idx = 8
    else:
        nickname_idx = 6
        nickname_flag_idx = 7
    nickname = word[nickname_idx]
    if word[nickname_flag_idx].find('H') != -1:
        nickname_flag = 'H'
    else:
        if word[nickname_flag_idx].find('G') != -1:
            nickname_flag = 'G'
        else:
            nickname_flag = ''
    if nickname_flag == '':
        hexchat.find_context().prnt('WARNING WRONG FLAG AT ' + network)
        hexchat.find_context().prnt(word[6] + word[7] + word[8])
        hexchat.find_context().prnt(word)
        hexchat.find_context().prnt('WARNING WRONG FLAG AT ' + network)
    if network in (AllUsers.keys()):
        if nickname in list(AllUsers[network].keys()):
            if AllUsers[network][nickname] != nickname_flag:
                if nickname_flag == 'H':
                    hexchat.find_context().prnt('\0034 *\t\002' + nickname + '\002 of ' + network + ' is \002\037here\002\037\003')
                else:
                    hexchat.find_context().prnt('\0034 *\t\002' + nickname + '\002 of ' + network + ' is \002\037gone\002\037\003')
                AllUsers[network][nickname] = nickname_flag
        else:
            AllUsers[network][nickname] = nickname_flag
    else:
        AllUsers[network] = {nickname: nickname_flag}

def debg(word,word_eol,userdata):
    print(list(AllUsers.keys()))
    print(ScanProgress)
    for network in list(AllUsers.keys()):
        hexchat.find_context().prnt(network + ' has ' + str(len(list(AllUsers[network].keys()))) + ' users.')
    return hexchat.EAT_HEXCHAT

def WhoScanStart(userdata):
    #print('timer started')
    global AllUsers
    global AllChannels
    for network in list(ScanProgress.keys()):
        if len(ScanProgress[network]) != 0:
            # hexchat.find_context().prnt('scan is in progress')
            return 1 # To keep the timer running
    AllChannels = {}
    allchannels = hexchat.get_list('channels')
    for channel in allchannels:
        if channel.type == 2:
            if channel.network not in list(AllChannels.keys()):
                AllChannels[channel.network] = [channel.channel]
            else:
                if channel.channel not in AllChannels[channel.network]:
                    AllChannels[channel.network].append(channel.channel)
    for network in list(AllUsers.keys()):
        if network not in list(AllChannels.keys()):
            del AllUsers[network]
    for network in list(AllChannels.keys()):
        #hexchat.find_context().prnt('scanning ' + AllChannels[network][0] + ' at ' + network)
        hexchat.find_context(server=network).command('WHO ' + AllChannels[network][0])
        ScanProgress[network] = AllChannels[network][0]
    return 1 # To keep the timer running

def WhoEND(word,word_eol,userdata):
    global AllChannels
    global ScanProgress
    network = hexchat.get_info('network')
    channel = word[3]
    if network not in list(ScanProgress.keys()):
        return
    if channel == ScanProgress[network]:
        #hexchat.find_context().prnt('finished ' + channel + ' at ' + network)
        chidx = AllChannels[network].index(channel)
        chidx += 1
        if chidx < len(AllChannels[network]):
            hexchat.find_context(server=network).command('WHO ' + AllChannels[network][chidx])
            ScanProgress[network] = AllChannels[network][chidx]
            #hexchat.find_context().prnt('scanning ' + AllChannels[network][chidx] + ' at ' + network)
        else:
            ScanProgress[network] = ''
            # hexchat.find_context().prnt('stopped at ' + network)

def UserQuit(word,word_eol,userdata):
    global AllUsers
    network = hexchat.get_info('network')
    nickname = word[0]
    if network in list(AllUsers.keys()):
        if nickname in list(AllUsers[network].keys()):
            del AllUsers[network][nickname]
def UserPart(word,word_eol,userdata):
    global AllUsers
    global AllChannels
    network = hexchat.get_info('network')
    nickname = word[0]
    channel = hexchat.get_info('channel')
    if network in list(AllUsers.keys()):
        for chan in list(AllChannels[network]):
            if chan != channel:
                users = hexchat.find_context(server=network, channel=chan).get_list('users')
                for user in users:
                    if nickname == user.nick:
                        return
        del AllUsers[network][nickname]

def UserKick(word,word_eol,userdata):
    global AllUsers
    global AllChannels
    network = hexchat.get_info('network')
    nickname = word[1]
    channel = hexchat.get_info('channel')
    if network in list(AllUsers.keys()):
        for chan in list(AllChannels[network]):
            if chan != channel:
                users = hexchat.find_context(server=network, channel=chan).get_list('users')
                for user in users:
                    if nickname == user.nick:
                        return
        del AllUsers[network][nickname]

def NickChange(word,word_eol,userdata):
    global AllUsers
    oldnick = word[0]
    newnick = word[1]
    network = hexchat.get_info('network')
    if oldnick in list(AllUsers[network].keys()):
        AllUsers[network][newnick] = AllUsers[network][oldnick]
        del AllUsers[network][oldnick]

hexchat.hook_command('TRY',debg)
hexchat.hook_server("352", WhoRPL)
hexchat.hook_server("315", WhoEND)
hexchat.hook_print('Part',UserPart)
hexchat.hook_print('Kick',UserKick)
hexchat.hook_print('Quit',UserQuit)
hexchat.hook_print('Change Nick',NickChange)
Timer_hk = hexchat.hook_timer(5000,WhoScanStart)
hexchat.hook_unload(unload_callback)
print("\0034" + __module_name__ + '\tVersion ' + __module_version__ + ' loaded.\003')
