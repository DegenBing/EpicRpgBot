#author : bing
import sys
import requests
import json
import random
import time

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

def command(cmd, channel=rpg_fight_thread, author="555955826880413696", limit=3):
    global tagMode
    if checkNotInJail() == False:
        help_jail()
        return
    msgJson = getMsg(channel)
    if msgJson == "":
        cmdLog("get null msg error : horde")
        return ""
    msg = json.dumps(msgJson)
    if "horde" in msg:
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

    msgs = getMsg(channel, limit)
    if msgs == "":
        cmdLog("get null msg error : cmd resp")
        return ""
    # for debug
    if author == "all":
        return msgs
    # return newest response from selected id
    for msg in msgs:
        if msg["author"]["id"] == author:
            #print("msg0", msg[0])
            return msg
    
    return ""

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
    command("a", "1026824974121566259")
    time.sleep(10)

def hunt(target):
    command("heal")
    command("area "+str(target))
    if huntH != "Off":
        command("hunt h")
    else :
        command("hunt")
    command("heal")

def adv(target):
    command("heal")
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
        command("farm")
        return

def petAdv():
    command("pets claim")
    command("pets adventure a")

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
    global huntH
    global advH

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
                huntH : On / Off, On -> huntH, Off -> hunt\n\
                advH : On / Off, On -> advH, Off -> adv")
    elif cmd == "stat":
        cmdLog("hunt : " + str(target_hunt)\
            +"\nadv : " + str(target_adv)\
            +"\nwork : " + str(target_work)\
            +"\nduel : " + str(duelTargetId)\
            +"\nsleepMode : " + sleepMode\
            +"\nsilentMode : " + silentMode\
            +"\ntagMode : " + tagMode\
            +"\nhuntH : " + huntH
            +"\nadvH : " + advH)
        cmdLog("ver : 11080800" )
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
    elif cmd == "setHuntH":
        huntH = cmds[1]
        cmdLog("setHuntH to " + huntH)
    elif cmd == "setAdvH":
        advH = cmds[1]
        cmdLog("setAdvH to " + advH)
    elif cmd == "setDuel":
        duelTargetId = cmds[1]
        cmdLog("set duel to " + duelTargetId)
    
    else:
        cmdLog("unknown cmd : " + cmd)

############ main  ################
telegram_bot_sendtext("epic rpg start")
nonce = 0

target_hunt = "13"
target_adv = "13"
#1-2 chop, 3-5 axe, 6-7 ladder, 8 bowsaw, 9-12 chainsaw / bigboat
target_work = "bigboat"

sleepMode = "Off"
silentMode = "Off"
tagMode = "Off"
huntH = "Off"
advH = "Off"

players = ["<@1021213720254353440>", "<@1025701583008309281>", "<@1013138128652996689>", "<@1013359726567882753>"]
playerName = ["SPD", "dod", "dio", "nina"]
duelTargetId = 2

chat("[bot]restart", self_cmd)

while True:
    try:
        if silentMode == "Off":
            getRd()
    except Exception as e:
        cmdLog("error" + str(e))        
    # log status every 10 min
    if not nonce%10 and silentMode != "Off":
        command("profile")
        command("inventory")
        command("pets adventure claim")
        command("pets adventure find a")
    nonce+=1
    # split it so no need to wait when stop
    for i in range(1,60):
        getSelfCmd()
        time.sleep(1)
