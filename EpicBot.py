#author : bing
import sys
import requests
import json
import random
import time
import re

############ vars #################

momo_bing = "1026824308783333437"
self_cmd = "1034708685328498689"

#epic helper = 812942851814064150
#epic rpg = 555955826880413696
epic_helper = "812942851814064150"

auth = sys.argv[1]
tgToken = sys.argv[2]
rpg_fight_thread = sys.argv[3]

header = {
    "Authorization": auth,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
}

########   basic msg funcs  ################
def chat(content, channel=rpg_fight_thread):
    msg = {
        "content": content,
        "nonce": "82329451214{}33232234".format(random.randrange(0, 1000)),
        "tts": False,
    }
    url = "https://discord.com/api/v9/channels/{}/messages".format(channel)
    try:
        res = requests.post(url=url, headers=header, data=json.dumps(msg))  
        #print(json.loads(res.content))
        return res
    except Exception as e:
        cmdLog("chat error : "+str(e))
        
def getMsg(channel=rpg_fight_thread, limit=3):
    #print("get msg from"+str(channel))
    url = "https://discord.com/api/v9/channels/{}/messages?limit={}".format(channel, limit)
    try:
        res = requests.get(url=url, headers=header)
        msg_json = json.loads(res.text)
        #print(msg_json)
        #for msg in msg_json:
            #print("aurthor : ", msg["author"]["username"], ", content : ", msg["content"])
        return msg_json
    except Exception as e:
        cmdLog("get msg error : " + str(e))
        return ""

def getAuthorMsg(channel=rpg_fight_thread, limit=5, author='555955826880413696'):
    msgs = getMsg(channel, limit)
    # return newest response from selected id
    for msg in msgs:
        if msg["author"]["id"] == author:
            return msg
    return ""

def command(cmd, channel=rpg_fight_thread):
    global tagMode
    if checkNotInJail() == False:
        help_jail()
        return

    msg = getAuthorMsg()
    #handle horde
    if "horde" in msg and hordeMode != "Off":
        if tagMode == "Off":
            chat("join", channel)
        else:
            chat("<@555955826880413696> join", channel)
        telegram_bot_sendtext("horde!")
        return
    
    if tagMode == "Off":
        chat("rpg "+cmd, channel)
    else:
        chat("<@555955826880413696> "+cmd, channel)
    time.sleep(1.5)
    # in case get in jail at last command
    if checkNotInJail() == False:
        help_jail()
        return

    return getAuthorMsg()

def checkNotInJail(channel=rpg_fight_thread):
    msgJson = getMsg(channel)
    if msgJson == "":
        cmdLog("get null msg error : check jail")
        return True
    msg = json.dumps(msgJson)
    if "jail" in msg:
        cmdLog("jail")
        return False
    if "rules" in msg:
        cmdLog("rule")
        return False
    if "image " in msg:
        cmdLog("image")
        return False
    #print(msg)
    return True

########   command logic ############
def getRd():
    global target_hunt
    global target_adv
    global target_work
    global sleepMode
    msg = command("rd")
    try:
        #ready_options = msg["embeds"][0]["fields"]
        string = json.dumps(msg) 
        if "ready" not in string:
            #got wrong response
            cmdLog(string)
            return 
        if "loot" in string:
            command("buy edgy lootbox")
        if "training" in string:
            train()
        if "duel" in string:
            duel()
        if sleepMode != "Off":
            # sleep mode, stop do cmd may get in jail
            return
        if "hunt" in string:
            hunt(target_hunt)
        if "adventure" in string:
            adv(target_adv)
        if "farm" in string and "Locked" not in string:
            farm()
        if "chop" in string:
            command(target_work)
        return
    except Exception as e:
        if "All your commands are on cooldown" in json.dumps(msg):
            cmdLog("cooldown " + json.dumps(msg))
            return        
        if "previous" in json.dumps(msg) :
            cmdLog("previous command " + json.dumps(msg))
            return
        if "spam" in json.dumps(msg) :
            cmdLog("spam " + json.dumps(msg))
            return
        #print("---something get in.---")
        if "TIP:" in json.dumps(msg):
            cmdLog("tip")
        else:
            cmdLog("unexpected error "+ str(e))
            cmdLog("last msg"+json.dumps(msg))
        getRd()

def duel():
    global tagMode
    # get duel target status
    res = command("cd " + players[int(duelTargetId)], channel=momo_bing)
    string = json.dumps(res)
    if "**`duel`** (" in string:
        cmdLog(playerName[int(duelTargetId)] + " cd ing")
        telegram_bot_sendtext(playerName[int(duelTargetId)] + " cd ing")
        return

    #print(playerName[duelTargetId] + " ready")
    command("duel "+players[int(duelTargetId)], channel="1026824974121566259")
    time.sleep(5)
    if tagMode == "Off":
        chat("a", "1026824974121566259")
    else:
        chat("<@555955826880413696> a", "1026824974121566259")
    time.sleep(10)

def hunt(target):
    command("heal")
    if dynArea != "Off":
        command("area "+str(target))
    if huntH != "Off":
        command("hunt h")
    else :
        command("hunt")
    command("heal")

def adv(target):
    command("heal")
    if dynArea != "Off":
        command("area "+str(target))
    if advH != "Off":
        command("adventure h")
    else :
        command("adventure")
    command("heal")

def farm():
    msg = command("i")
    if msg != "":
        string = json.dumps(msg)
        if "carrot seed" in string:
            command("farm carrot")
            return
        # only farm other if carrotMode Off
        if "bread seed" in string and carrotMode == "Off":
            command("farm bread")
            return
        if "potato seed" in string and carrotMode == "Off":
            command("farm potato")
            return
        command("farm")
        return

def petAdv():
    command("pets adv claim")
    for cmd in petCmds:
        command(cmd)

def train():
    command("trade e all")
    msg = command("tr")
    string = json.dumps(msg)
    ans = getTrainAns(string)
    cmdLog("training str:"+string)
    cmdLog("ans:"+ans)
    chat(ans)
    time.sleep(1.5)
    #send 2 time in case miss it
    chat(ans)
    time.sleep(1.5)
    #check pet
    msg = json.dumps(getAuthorMsg()).replace("*","")
    if "APPROACHING" in msg:
        telegram_bot_sendtext("pet!")
        cmdLog("pet msg : "+msg)
        time.sleep(0.5)
        ans = catch_pet(msg)
        cmdLog("pet ans : "+ans)
        chat(ans)    
        #send 2 time in case miss it
        time.sleep(1.5)
        chat(ans)

def catch_pet(msg) :
    ans = ''
    hunger = int(re.search('Hunger: (\d+)', msg).group(1))
    n1 = int( ( hunger + 10 ) / 20 ) 
    ans = 'feed ' * n1

    happy = int( re.search('Happiness: (\d+)', msg).group(1) )
    n2 = int( ( 100 - happy ) / 10 )

    n2 = n2 if (n1 + n2) <= 6 else 6 - n1
    ans += 'pat ' * n2

    return ans

def getTrainAns(message):
    if "field!" in message:
        tmp = re.search('(\w+).. letter of <:(\w+):', message)
        num = { 
            'first'  : 0,
            'second' : 1,
            'third'  : 2,
            'fourth' : 3,
            'fifth'  : 4,
            'sixth'  : 5
        }
        return str(tmp.group(2).upper()[num[tmp.group(1)]])

    if "river!" in message :
        tmp = re.search('<:(\w+):', message)
        fish = {
            'normiefish' : 1,
            'goldenfish' : 2,
            'EPICfish'   : 3
        }
        return str(fish[tmp.group(1)])

    if "mine!" in message :
        return "N"
    
    if "casino?" in message :
        #erase space to handle four leaf
        nMsg = message.replace(" ","")
        nMsg = nMsg.replace("*","")
        tmp = re.search('thisa(\w+)\?.(\w+).\\n', nMsg )
        if tmp == None :
            return "N"

        pair = {
            'diamond' : 'gem',
            'dice'    : 'game_die',
            'gift'    : 'gift',
            'fourleafclover'    : "four_leaf_clover",
            "coin"    : 'coin'
        }

        ask = "".join(tmp.group(1).split(" ")).lower()
        if ask in pair :
            ask = pair[ask]
        
        if ask == tmp.group(2):
            return "Y"
        return "N"

    if "forest!" in message :
        key = re.search('many <:(\w+):', message).group(1)
        tmp = re.findall( '<:'+key+':', message)
        return str( len(tmp) - 1 )

    return None

#############  tg alert ###########

def telegram_bot_sendtext(bot_message):
    bot_chatID = '1212111353'
    send_text = 'https://api.telegram.org/bot' + tgToken + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)
    return response.json()

def help_jail(msg=""):
    telegram_bot_sendtext("jail 995" + msg)
    time.sleep(5)

##########   bot setting ###########

def getSelfCmd():
    cmd = getMsg(self_cmd,1)[0]["content"]
    if cmd == "":
        return
    if cmd[0:5] == "[bot]":
        #print("no new")
        return
    #print("cmd :"+cmd)
    #cmdLog("get new cmd : " + cmd)
    execCmd(cmd)

def cmdLog(log):
    chat("[bot]"+log, self_cmd)

def execCmd(cmds):
    global target_hunt
    global target_adv
    global target_work
    global duelTargetId
    global sleepMode
    global silentMode
    global tagMode
    global carrotMode
    global hordeMode
    global dynArea
    global huntH
    global advH
    global petCmds

    cmds = cmds.split(" ")
    cmd = cmds[0]
    if cmd == "help":
        cmdLog("stat : get current stats\n\
                setAdv : set adv area\n\
                setHunt : setHuntArea\n\
                setWork : setWorkCmd (1-2 chop, 3-5 axe, 6-7 ladder, 8 bowsaw, 9-12 chainsaw / bigboat)\n\
                setDuel : setDuel (0 SPD, 1 dod, 2 dio, 3 nina )\n\
                setSleep : On / Off, On -> only loot and duel\n\
                setSilent : On / Off, On -> do nothing\n\
                setTag : On / Off, On -> tag epic bot\n\
                setCarrot : On / Off, On -> only carrot\n\
                setDynArea : On / Off, On -> check area before hunt/adv\n\
                setHorde : On / Off, On -> join horde\n\
                huntH : On / Off, On -> huntH, Off -> hunt\n\
                advH : On / Off, On -> advH, Off -> adv\n\
                resetPet : reset pet find target\n\
                addPet : addPet Cmd (ex : find a)\n\
                forcePet : force call petAdv()")
    elif cmd == "stat":
        cmdLog("hunt : " + str(target_hunt)\
            +"\nadv : " + str(target_adv)\
            +"\nwork : " + str(target_work)\
            +"\nduel : " + str(duelTargetId)\
            +"\nsleepMode : " + sleepMode\
            +"\nsilentMode : " + silentMode\
            +"\ntagMode : " + tagMode\
            +"\ncarrotMode : " + carrotMode\
            +"\nhordeMode : " + hordeMode\
            +"\ndynArea : " + dynArea\
            +"\nhuntH : " + huntH
            +"\nadvH : " + advH
            +"\npetCmd : "+ str(petCmds))
        cmdLog("ver : "+str(versionNum))
    elif cmd == "setHunt":
        try:
            new_target_hunt = int(cmds[1])
        except Exception as e:
            cmdLog("setHunt err "+str(e))
            return
        target_hunt = new_target_hunt
        cmdLog("setHunt to " + str(target_hunt))
    elif cmd == "setAdv":
        try:
            new_target_adv = int(cmds[1])
        except Exception as e:
            cmdLog("setAdv err "+str(e))
            return
        target_adv = new_target_adv
        cmdLog("setAdv to " + str(target_adv))
    elif cmd == "setWork":
        target_work = cmds[1]
        cmdLog("setWork to " + target_work)
    elif cmd == "setSleep":
        sleepMode = cmds[1]
        cmdLog("setSleep to " + sleepMode)
    elif cmd == "setSilent":
        silentMode = cmds[1]
        cmdLog("setSilent to " + silentMode)
    elif cmd == "setTag":
        tagMode = cmds[1]
        cmdLog("setTag to " + tagMode)
    elif cmd == "setCarrot":
        carrotMode = cmds[1]
        cmdLog("setCarrot to " + carrotMode)
    elif cmd == "setHorde":
        hordeMode = cmds[1]
        cmdLog("setHorde to " + hordeMode)
    elif cmd == "setDynArea":
        dynArea = cmds[1]
        cmdLog("setDynArea to " + dynArea)
    elif cmd == "setHuntH":
        huntH = cmds[1]
        cmdLog("setHuntH to " + huntH)
    elif cmd == "setAdvH":
        advH = cmds[1]
        cmdLog("setAdvH to " + advH)
    elif cmd == "setDuel":
        duelTargetId = cmds[1]
        cmdLog("set duel to " + duelTargetId)
    elif cmd == "resetPet":
        petCmds = ["pet adv find "+cmds[1]]
        cmdLog("reset pet cmd to " + str(petCmds))
    elif cmd == "addPet":
        cmdstr = "pet adv " + cmds[1] + " " + cmds[2]
        petCmds.append(cmdstr)
        cmdLog("add pet : " + str(cmdstr))
        cmdLog("cur pet cmd :" + str(petCmds))
    elif cmd == "forcePet":
        petAdv()
        cmdLog("force pet")
    else:
        cmdLog("unknown cmd : " + cmd)

############ main  ################
telegram_bot_sendtext("epic rpg start")
nonce = 0

versionNum = "01051300"

target_hunt = "13"
target_adv = "13"
#1-2 chop, 3-5 axe, 6-7 ladder, 8 bowsaw, 9-12 chainsaw / bigboat
target_work = "dynamite"

sleepMode = "On"    # default sleep, in case crash/restart when sleeping
silentMode = "Off"
tagMode = "Off"
carrotMode = "Off"
hordeMode = "Off"
dynArea = "Off"     # default not change area
huntH = "On"
advH = "On"
petCmds = ["pet adv find h"]

players = ["<@1021213720254353440>", "<@1025701583008309281>", "<@955368738180440076>", "<@1013138128652996689>", "<@1013359726567882753>"]
playerName = ["SPD", "dod", "raphel", "dio", "nina"]
duelTargetId = 2

chat("[bot]restart", self_cmd)

while True:
    # if silent mode or sleep mode on, don't rd every min.
    try:
        if silentMode == "Off" and sleepMode == "Off":
            getRd()
    except Exception as e:
        cmdLog("error" + str(e))        
    # log status every 10 min and pet adv if silentMode off
    if not nonce%10 and silentMode == "Off":
        getRd()
        command("profile")
        command("inventory")
        petAdv()
    nonce+=1
    # split it so no need to wait when stop
    for i in range(1,60):
        getSelfCmd()
        time.sleep(1)
