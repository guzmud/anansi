#! /usr/bin/python

##### IMPORT IMPORT IMPORT #####

## CANON IMPORTS
import multiprocessing, ctypes, os, inspect

## HOMEBREW LIBS
import lib_workers as workers

##### VARS VARS VARS #####

SPIDERNEST = [] # will be populated with the workers
IS_RUNNING = True # is the whole Anansi running
NET_ENGINE = False # is the net engine runninh
CRAFT = None # which craft is on
APPLICATION = None # which application is on

##### FX #####

def killswitch_all():

    global NET_ENGINE, CRAFT, APPLICATION
    
    print "\nANANSI : killswitch activated, for all !"
    for i in SPIDERNEST:
        print "\tANANSI : killing "+str(i)
        i.is_running = False
        i.terminate()
        i.join()

    NET_ENGINE = False
    CRAFT = None
    APPLICATION = None

def killswitch_bytype(wtype):

    global NET_ENGINE, CRAFT, APPLICATION
    
    print "\nANANSI : killswitch activated for "+str(wtype)+" spiders"
    for i in SPIDERNEST:
        if (i.wtype == wtype):
            print "\tANANSI : killing "+str(i)
            i.is_running = False
            i.terminate()
            i.join()
    
    if wtype == "engine":
        NET_ENGINE = False
    elif wtype == "craft":
        CRAFT = None
    elif wtype == "application":
        APPLICATION = None

def workerstatus():
    print "\nANANSI : spiders status"
    for i in SPIDERNEST:
        print "\tANANSI : "+str(i)

def workerstatus_bytype(wtype):
    print "\nANANSI : "+str(wtype)+" spiders status"
    for i in SPIDERNEST:
        if (i.wtype == wtype):
            print "\tANANSI : "+str(i)

def workercount_bytype(wtype):
    k = 0
    for i in SPIDERNEST:
        if ((i.is_running) and (i.wtype == wtype)):
            k += 1
    return k

## NET

def netprobe_start():

    print "\nANANSI : starting probe spider"
    num = 3
    while num not in [0,1,2]:
        try:
            num = int(raw_input("> Please, choose the device : dev0 (0), dev1 (1), cancel probe (2)\n"))
        except Exception:
            print "\nANANSI : Sorry, I could not understand your answer"
            num = 3
    if num in [0,1]:
        vb = str(raw_input("> Verbose [y/n] ? (achtung, will print every packet content)\n"))
        bvb = False
        if vb.lower() == 'y':
            bvb = True
        db = workers.ProbeSpider(num,verbose=bvb)
        SPIDERNEST.append(db)
        db.start()
        print str(db)+" started"
    else:
        print "\nANANSI : ProbeSpider cancelled"

def netengine_start():

    global NET_ENGINE
    
    print "\nANANSI : starting the net engine"
    
    sr0 = workers.ReadingSpider(0)
    SPIDERNEST.append(sr0)
    sr0.start()
    print "\nANANSI : reading spider 0 started"

    sm0 = workers.MiddleSpider(0)
    SPIDERNEST.append(sm0)
    sm0.start()
    print "\nANANSI : middle spider 0 started"

    sw0 = workers.WritingSpider(0)
    SPIDERNEST.append(sw0)
    sw0.start()
    print "\nANANSI : writing spider 0 started"

    sr1 = workers.ReadingSpider(1)
    SPIDERNEST.append(sr1)
    sr1.start()
    print "\nANANSI : reading spider 1 started"

    sm1 = workers.MiddleSpider(1)
    SPIDERNEST.append(sm1)
    sm1.start()
    print "\nANANSI : middle spider 1 started"

    sw1 = workers.WritingSpider(1)
    SPIDERNEST.append(sw1)
    sw1.start()
    print "\nANANSI : writing spider 1 started"

    NET_ENGINE = True

## SCENARIOS
    # /!\ A RETRAVAILLER POUR LA SEPARATION STEG ET APPLI (PASSER DE STEG A CRAFT ?)

def changeScenario():
    print "\nANANSI : stegconf.py => stegconf.py.old (backup)"
    print "\nANANSI : new scenario (from 'scenarios' folder) => stegconf.py"
    scenario_name = str(raw_input("\nANANSI : scenario name ? (extension not included, eg. 'canonical')\n> "))
    workers.changeScenar(scenario_name)
    print "\nANANSI : refreshing the global variables"
    workers.loadConf()

def checkScenario():
    scenario_name = str(raw_input("\nANANSI : scenario name ? (extension not included, eg. 'canonical')\n> "))
    description = workers.checkScenar(scenario_name)
    print "\nANANSI : "+str(scenario_name)+"\n"+str(description)

def genScenariosList():
    slist = []
    tpath = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),workers.SCENARIO_FOLDER,workers.STEGSCENAR_FOLDER)
    for i in os.listdir(tpath):
        if ".pyc" not in i:
            if "__init__" not in i:
                slist += [i]
    return slist

def getScenariosList():
    print "\nANANSI : looking for *.py in "+str(workers.SCENARIO_FOLDER)+"/"+str(workers.STEGSCENAR_FOLDER)
    slist = genScenariosList()
    print "\nANANSI : "+', '.join(slist)

## CRAFT

def nocraft_start():

    global CRAFT

    sc0 = workers.NoviceSpider(0)
    SPIDERNEST.append(sc0)
    sc0.start()
    print "\nANANSI : crafting spider 0 started"

    sc1 = workers.NoviceSpider(1)
    SPIDERNEST.append(sc1)
    sc1.start()
    print "\nANANSI : crafting spider 1 started"

    CRAFT = "novice (no craft)"

def stegcraft_start():

    global CRAFT

    sc0 = workers.StegSpider(0)
    SPIDERNEST.append(sc0)
    sc0.start()
    print "\nANANSI : crafting spider 0 started"

    sc1 = workers.StegSpider(1)
    SPIDERNEST.append(sc1)
    sc1.start()
    print "\nANANSI : crafting spider 1 started"

    CRAFT = "stegano"

## APPLICATION

def spam_start():

    global APPLICATION

    print "\nSPAM : sending k random bits on the wire"
    k = int(raw_input("\nSPAM : value of k ?\n>"))
    sks = workers.SpamSpider(k)
    SPIDERNEST.append(sks)
    sks.start()

    APPLICATION = "spam"

def chat_start():

    global APPLICATION

    print "WELCOME TO THE POINT-TO-POINT CHAT"
    print "(please tape EXIT to end the conversation)"

    sa0 = workers.ShamirChatSpider(0)
    SPIDERNEST.append(sa0)
    sa0.start()

    sa1 = workers.ShamirChatSpider(1)
    SPIDERNEST.append(sa1)
    sa1.start()

    APPLICATION = "chat"

## INTERFACE ##

def splash_screen():
    splashcii = """
   ('-.         .-') _    ('-.         .-') _   .-')
  ( OO ).-.    ( OO ) )  ( OO ).-.    ( OO ) ) ( OO ).           
  / . --. /,--./ ,--,'   / . --. /,--./ ,--,' (_)---\_)  ,-.-')  
  | \-.  \ |   \ |  |\   | \-.  \ |   \ |  |\ /    _ |   |  |OO) 
.-'-'  |  ||    \|  | ).-'-'  |  ||    \|  | )\  :` `.   |  |  \ 
 \| |_.'  ||  .     |/  \| |_.'  ||  .     |/  '..`''.)  |  |(_/ 
  |  .-.  ||  |\    |    |  .-.  ||  |\    |  .-._)   \ ,|  |_.' 
  |  | |  ||  | \   |    |  | |  ||  | \   |  \       /(_|  |    
  `--' `--'`--'  `--'    `--' `--'`--'  `--'   `-----'   `--'    """
    print splashcii

def header():
    print "\n################################"
    print "\tANANSI\n"

def main_header():
    print "DEVICE 0       : "+str(workers.DEV0IP)
    print "DEVICE 1       : "+str(workers.DEV1IP)
    print "NET ENGINE     : "+str(NET_ENGINE)+" ("+str(workercount_bytype("engine"))+" spiders)"
    print "SCENARIO       : "+str(workers.SCENARIO_NAME)
    print "CRAFT          : "+str(CRAFT)+" ("+str(workercount_bytype("craft"))+" spiders)"
    print "APPLICATION    : "+str(APPLICATION)+" ("+str(workercount_bytype("application"))+" spiders)"
    print "################################\n"

def engine_header():
    print "DEVICE 0       : "+str(workers.DEV0IP)
    print "DEVICE 1       : "+str(workers.DEV1IP)
    print "NET ENGINE     : "+str(NET_ENGINE)+" ("+str(workercount_bytype("engine"))+" spiders)"
    print [x for x in SPIDERNEST if (x.wtype == "engine" and x.is_running)]
    print "################################\n"

def craft_header():
    print "SCENARIO       : "+str(workers.SCENARIO_NAME)
    print "SCENARIOS LIST : "+str(genScenariosList())
    print "CRAFT          : "+str(CRAFT)+" ("+str(workercount_bytype("craft"))+" spiders)"
    print [x for x in SPIDERNEST if (x.wtype == "craft" and x.is_running)]
    print "################################\n"

def application_header():
    print "APPLICATION    : "+str(APPLICATION)+" ("+str(workercount_bytype("application"))+" spiders)"
    print [x for x in SPIDERNEST if (x.wtype == "application" and x.is_running)]
    print "################################\n"

def main_menu():
    
    global IS_RUNNING
    
    while IS_RUNNING:
        header()
        main_header()
        print "MAIN MENU"
        print "\t0. Leave Anansi"
        print "\t1. Engine menu"
        print "\t2. Scenario menu"
        print "\t3. Craft menu"
        print "\t4. Application menu"
        print "\t5. Maintenance menu"
        print ""
        temp = str(raw_input("ANANSI : Please, choose.\n> "))

        if temp == '0':
            killswitch_all() # safety first
            workers.close_queues() # avant ou apres killswitch ?
            workers.close_handlers()
            IS_RUNNING = False
        elif temp == '1':
            engine_menu()
        elif temp == '2':
            scenario_menu()
        elif temp == '3':
            craft_menu()
        elif temp == '4':
            application_menu()
        elif temp == '5':
            maintenance_menu()
        else:
            print "ANANSI : sorry, I can't understand "+temp
        print ""

    print "Leaving Anansi ..."

def engine_menu():
    temp = '5'
    while temp != '0':
        header()
        engine_header()
        print "ENGINE MENU"
        print "\t0. Main menu"
        print "\t1. Engine spiders status"
        print "\t2. Engine : net engine spiders"
        print "\t3. Engine : net probe spider"
        print "\t4. Kill engine spiders"
        print ""
        temp = str(raw_input("ANANSI : Please, choose.\n> "))
        if temp == '0':
            main_menu()
        elif temp == '1':
            workerstatus_bytype("engine")
        elif temp == '2':
            netengine_start()
        elif temp == '3':
            netprobe_start()
        elif temp == '4':
            killswitch_bytype("engine")
        else:
            print "ANANSI : Sorry, I can't understand "+temp

def scenario_menu():
    temp = '8'
    while temp != '0':
        header()
        craft_header()
        print "SCENARIO MENU"
        print "\t0. Main menu"
        print "\t1. Get scenarios list"
        print "\t2. Check scenario"
        print "\t3. Change scenario"
        print ""
        temp = str(raw_input("ANANSI : Please, choose.\n> "))
        if temp == '0':
            main_menu()
        elif temp == '1':
            getScenariosList()
        elif temp == '2':
            checkScenario()
        elif temp == '3':
            changeScenario()
        else:
            print "ANANSI : Sorry, I can't understand "+temp

def craft_menu():
    temp = '8'
    while temp != '0':
        header()
        craft_header()
        print "CRAFT MENU"
        print "\t0. Main menu"
        print "\t1. Craft spiders status"
        print "\t2. Craft : novice spider (no craft)"
        print "\t3. Craft : stegano spider"
        print "\t4. Kill craft spiders"
        print ""
        temp = str(raw_input("ANANSI : Please, choose.\n> "))
        if temp == '0':
            main_menu()
        elif temp == '1':
            workerstatus_bytype("craft")
        elif temp == '2':
            nocraft_start()
        elif temp == '3':
            stegcraft_start()
        elif temp == '4':
            killswitch_bytype("craft")
        else:
            print "ANANSI : Sorry, I can't understand "+temp

def application_menu():
    temp = '5'
    while temp != '0':
        header()
        application_header()
        print "APPLICATIONS MENU"
        print "\t0. Main menu"
        print "\t1. Application spiders status"
        print "\t2. Application : spam spider"
        print "\t3. Application : Shamir chat spider"
        print "\t4. Kill application spiders"
        print ""
        temp = str(raw_input("ANANSI : Please, choose.\n> "))
        if temp == '0':
            main_menu()
        elif temp == '1':
            workerstatus_bytype("application")
        elif temp == '2':
            spam_start()
        elif temp == '3':
            chat_start()
        elif temp == '4':
            killswitch_bytype("application")
        else:
            print "ANANSI : Sorry, I can't understand "+temp

def maintenance_menu():
    temp = '5'
    while temp != '0':
        header()
        main_header()
        print "MAINTENANCE MENU"
        print "\t0. Main menu"
        print "\t1. Kill all spiders"
        print "\t2. Restart all queues"
        print "\t3. Restart pcap handlers"
        temp = str(raw_input("ANANSI : Please, choose.\n> "))
        if temp == '0':
            main_menu()
        elif temp == '1':
            killswitch_all()
        elif temp == '2':
            workers.restart_queues()
        elif temp == '3':
            workers.restart_handlers()
        else:
            print "ANANSI : Sorry, I can't understand "+temp

##### MAIN MAIN MAIN #####

if __name__ == '__main__':
    splash_screen()
    main_menu()
