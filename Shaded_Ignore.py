__module_name__ = "Shaded Ignore"
__module_version__ = "0.001"
__module_description__ = "Show messages from ignored users with shadowed color"

#http://i.imgur.com/wVB9DAV.png?1
#adding nick,network to the list:
#check if the nick is in prefs
#check if network exist
#check if nick exist in that network
#store the nick and network in prefs

#adding nick only to the list:
    #do the same thing

import hexchat

shign_prefix = 'shign'
nick_idx = 0
network_idx = 0
shign_list = []
shign_list_last_idx = 0
def nethelp():
    return __module_name__ + '\tUsage: /SHIGNNET, List all online networks'

def listhelp():
    return __module_name__ + '\tUsage: /SHIGNLIST, List all ignored entries'
def addhelp():
    return __module_name__ + '\tUsage: /SHIGNADD <nick> <network>, Add nick to list with network. If network is ommitted, it will be ignored on all networks'
def delhelp():
    return __module_name__ + '\tUsage: /SHIGNDEL <nick> <network>, Deletes a nickname from the list. If network is ommitted, it will be removed from all networks'

#shign0 = network nick1 nick2 nick3
#shign_pluginpref_list = [shing0, shign1, shign2, ... ,shignN]
#shign_list = [[shing0, network1, nick1, nick2, nick3, ...], [shing1, network1, nick1, nick2, nick3, ...], ... [shingN, networkN, nick1, nick2, nick3, ...]]
def shign_load_list(word=None,word_eol=None,userdata=None):
    global shign_prefix
    global shign_pluginpref_list
    global shign_list
    global shign_list_last_idx
    All_Prefs = hexchat.list_pluginpref()
    shign_pluginpref_list = []
    shign_list = []
    shign_list_last_idx = 0
    if len(All_Prefs) == 0:
        #print('empty') #list is empty
        shign_list = [['shign1','All']]
        hexchat.set_pluginpref('shign1','All')
        shign_list_last_idx = 1
        return
    for Prefs in All_Prefs:
        if Prefs.find(shign_prefix) != -1: #if the prefix is found
            shign_pluginpref_list.append(Prefs) #append to the list of prefs
            if int(Prefs[5:]) > shign_list_last_idx:
                shign_list_last_idx = int(Prefs[5:])
    #print(shignpreflist)
    for shign_pluginpref in shign_pluginpref_list:
        temp_list = hexchat.get_pluginpref(shign_pluginpref).split()
        temp_list.insert(0, shign_pluginpref)
        shign_list.append(temp_list)
    print(__module_name__+'\tList loaded!')

def shign_add_list(word,word_eol,userdata):
    global shign_list
    global shign_list_last_idx
    global shign_prefix
    network_found = 0
    if len(word) <= 3 and len(word) > 1: 
        if len(word) == 3: #network provided
            IgnoredNick = word[1]
            IgnoredNetwork = word[2]
        else:
            if len(word) == 2:#netowkr isn't provided, assuming network is 'All'
                IgnoredNick = word[1]
                IgnoredNetwork = 'All'
        for item in shign_list:
            if item[1].lower() == 'all' and IgnoredNick.lower() in [j.lower() for j in item[2:]]:
                print(__module_name__+'\tAlready ignored on all networks')
                return
            if item[1].lower() == IgnoredNetwork.lower():
                network_found = 1
                if item[1].lower() == IgnoredNetwork.lower() and IgnoredNick.lower() in [j.lower() for j in item[2:]]:
                    print(__module_name__+'\tAlready exists in the list')
                    return
                else:
                    network_idx = shign_list.index(item)
                    shign_list[network_idx].append(IgnoredNick)
                    hexchat.set_pluginpref(shign_list[network_idx][0],' '.join(shign_list[network_idx][1:]))
                    print(__module_name__+'\tAdded',word[1],'to',IgnoredNetwork)
                    if IgnoredNetwork == 'All':
                        for m in shign_list[1:]:
                            if IgnoredNick.lower() in [j.lower() for j in m[2:]]:
                                hexchat.command('SHIGNDEL ' + IgnoredNick + ' ' + m[1])
                break
            else:
                network_found = 0
                continue
        else:
            if network_found == 0:
                shign_list_last_idx += 1
                temp_list = [shign_prefix + str(shign_list_last_idx), IgnoredNetwork, IgnoredNick]
                shign_list.append(temp_list)
                hexchat.set_pluginpref(temp_list[0],' '.join(temp_list[1:]))
                print(__module_name__+'\tAdded',word[1],'to',IgnoredNetwork)
    else:
        if len(word) > 3:
            print(__module_name__+'\tInvalid syntax. ==>',word_eol[3])
            print(addhelp())
        else:
            print(addhelp())

def shign_del_list(word,word_eol,userdata):
    global shign_list
    global shign_list_last_idx
    if len(word) <= 3 and len(word) > 1:
        if len(word) == 2: #nick only provided
            nick_found = 0
            for item in shign_list:
                if word[1].lower() in [j.lower() for j in item[2:]]:
                    nick_found = 1
                    for k in shign_list[shign_list.index(item)]:
                        if k.lower() == word[1].lower():
                            shign_list[shign_list.index(item)].pop(shign_list[shign_list.index(item)].index(k))
                            hexchat.set_pluginpref(item[0],' '.join(item[1:]))
                            print(__module_name__+'\tRemoved',word[1],'from',item[1])
                            break
            else:
                if nick_found == 0:
                    print(__module_name__ + '\tNickname not found. Try /SHIGNLIST')
        if len(word) == 3: #nick and network provided
            #word[1] is the nickname
            #word[2] is the network
            network_found = 0
            for item in shign_list:
                if item[1].lower() == word[2].lower():
                    network_found = 1
                    if word[1].lower() in [j.lower() for j in item[2:]]:
                        nick_found = 1
                        for k in shign_list[shign_list.index(item)]:
                            if k.lower() == word[1].lower():
                                shign_list[shign_list.index(item)].pop(shign_list[shign_list.index(item)].index(k))
                                hexchat.set_pluginpref(item[0],' '.join(item[1:]))
                                print(__module_name__+'\tRemoved',word[1],'from',item[1])
                                break
                    else:
                        print(__module_name__ + '\tNickname not found in',item[1],'network. Try /SHIGNLIST')
                    break
            else:
                if network_found == 0:
                    print(__module_name__ + '\tNetwork not found. Try /SHIGNLIST')
    else:
        print(__module_name__ + '''\tUsage: /SHIGNDEL <nick> <network>, Delete nickname from a network
       If network is ommitted, nickname will be deleted from all networks''')

def shign_print_list(word,word_eol,userdata):
    global shign_list_last_idx
    print('\002\037\0034'+__module_name__+'\tList:\003\002\037')
    for item in shign_list:
        print('\002\037' + item[1] + ':\002\037')
        for i in item[2:]:
            print(str(item.index(i) - 1) + '.',i)

def shign_print_networks_list(word,word_eol,userdata):
    nets_list = []
    channels = hexchat.get_list('channels')
    for channel in channels:
        if channel.type == 1:
            if channel.network not in nets_list:
                nets_list.append(channel.network)
    print('\002\037\0034'+__module_name__+'\tNetworks List:\003\002\037')
    for item in nets_list:
        print(str(nets_list.index(item)) + '.', item)

def shign_shade(word,word_eol,userdata):
    #print(hexchat.strip(word[0]))
    #print(hexchat.get_info('network'))
    nick_color = word[0]
    nick = hexchat.strip(word[0])
    text = hexchat.strip(word[1])
    current_network = hexchat.get_info('network')
    if hexchat.strip(word[0]).lower() in [i.lower() for i in shign_list[0][2:]]:
        print(nick_color + '\t\0031,1' + text)
        return hexchat.EAT_ALL
    else:
        for item in shign_list[1:]:
            if current_network.lower() == item[1].lower() and nick.lower() in [i.lower() for i in item[2:]]:
                print(nick_color + '\t\0031,1' + text)
                return hexchat.EAT_ALL
                break

def unload_callback(userdata):
    print("\0034"+__module_name__ +'\tversion ' + __module_version__ + ' unloaded.\003')

#hexchat.hook_command('SHIGNRELOAD',shign_load_list,help=ignhelp())
hexchat.hook_command('SHIGNADD',shign_add_list,help=addhelp())
hexchat.hook_command('SHIGNDEL',shign_del_list,help=delhelp())
hexchat.hook_command('SHIGNLIST',shign_print_list,help=listhelp())
hexchat.hook_command('SHIGNNET',shign_print_networks_list,help=nethelp())
hexchat.hook_print('Channel Message',shign_shade)
hexchat.hook_unload(unload_callback)
shign_load_list()
print('\0034'+__module_name__+'\tversion '+__module_version__,'has been loaded.\003')
