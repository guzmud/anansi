#! /usr/bin/python

#### LIBS ####

## CANON IMPORTS
import ctypes, multiprocessing, threading
import time, math, shutil, os
import random, importlib, inspect

## EXT IMPORTS
import winpcapy

## HOMEBREW LIBS
import conf_net as netconf
import conf_steg as stegconf
import conf_appli as appliconf
import lib_net as netlib
import lib_steg as steglib
import lib_shamir as shamirlib
import lib_packetparser as packetparser

#### VARS ####

# SCENARIO VARS

DEFAULT_STEGCONF = 'conf_steg.py'
BACKUP_STEGCONF = 'conf_steg.py.old'
DEFAULT_APPLICONF = 'conf_appli.py'
BACKUP_APPLICONF = 'conf_appli.py.old'

SCENARIO_FOLDER = 'scenarios'
STEGSCENAR_FOLDER = 'steg'
APPLISCENAR_FOLDER ='appli'
SCENARIO_NAME = None

# PCAP VARS

ERRBUF = winpcapy.create_string_buffer(winpcapy.PCAP_ERRBUF_SIZE)

DEV0 = netconf.DEVICE1
DEV1 = netconf.DEVICE2
DEV0MAC = netconf.DEV1MAC
DEV1MAC = netconf.DEV2MAC
DEV0IP = netconf.DEV1IP
DEV1IP = netconf.DEV2IP

DEV0HANDLER = winpcapy.pcap_open_live(DEV0,65536,0,1000,ERRBUF)
DEV1HANDLER = winpcapy.pcap_open_live(DEV1,65536,0,1000,ERRBUF)

# BUFFER VARS

DEV0RBUFFER = multiprocessing.Queue() # buffer entre readingspider et craftspider
DEV0MBUFFER = multiprocessing.Queue() # buffer entre craftspider et middlespider
DEV0CBUFFER = multiprocessing.Queue() # buffer entre applispider et craftspider
DEV1WBUFFER = multiprocessing.Queue() # buffer entre middlespider et writing spider

DEV1RBUFFER = multiprocessing.Queue() # buffer entre readingspider et craftspider
DEV1MBUFFER = multiprocessing.Queue() # buffer entre craftspider et middlespider
DEV1CBUFFER = multiprocessing.Queue() # buffer entre applispider et craftspider
DEV0WBUFFER = multiprocessing.Queue() # buffer entre middlespider et writing spider

DEV0ABUFFER = multiprocessing.Queue() # buffer interne application
DEV1ABUFFER = multiprocessing.Queue() # buffer interne application

# STEGOSYSTEME
STEG_ENGINE_IS_ON = stegconf.STEG_ENGINE_IS_ON
F_NIV3_STEG = stegconf.F_NIV3_STEG
F_NIV4_STEG = stegconf.F_NIV4_STEG

# APPLI
SRC_FILEPATH = appliconf.SRC_FILEPATH
DST_FILEPATH = appliconf.DST_FILEPATH

# SHAMIR
SHAMIR_ON = appliconf.SHAMIR_ON
SHAMIR_N = appliconf.SHAMIR_N
SHAMIR_K = appliconf.SHAMIR_K
SHAMIR_GFIELD = appliconf.SHAMIR_GFIELD
SHAMIR_MLR = appliconf.SHAMIR_MAX_LETTER_REF

O_ABSCISSE_SIZE = int(math.log(SHAMIR_N,2))+1
O_ORDONNEE_SIZE = 7 # Y modulo is SHAMIR_GFIELD, hence 67, hence 7 bits # should automatise calculus

# MSEQUENCE
MSEQUENCE_ON = appliconf.MSEQUENCE_ON
MS_KEY_PERIOD = appliconf.MS_KEY_PERIOD
MS_TAPS = appliconf.MS_TAPS

# PROTOCOL
FLAG_STRING = appliconf.FLAG_STRING
FLAG_METHOD = appliconf.FLAG_METHOD
FLAG_FREQ = appliconf.FLAG_FREQ
REF_LETTER = appliconf.REF_LETTER
O_HEADER_SIZE = REF_LETTER+1

# FILTERS
F_NIV3 = stegconf.F_NIV3
PROTO3 = stegconf.PROTO3

F_NIV3_SRC = stegconf.F_NIV3_SRC
F_NIV3_DST = stegconf.F_NIV3_DST

F_NIV4 = stegconf.F_NIV4
PROTO4 = stegconf.PROTO4

#### FX ####

## PCAP FX

def close_handlers():
    winpcapy.pcap_close(DEV0HANDLER)
    winpcapy.pcap_close(DEV1HANDLER)

def restart_handlers():
    global DEV0HANDLER, DEV1HANDLER
    
    DEV0HANDLER = winpcapy.pcap_open_live(DEV0,65536,0,1000,ERRBUF)
    DEV1HANDLER = winpcapy.pcap_open_live(DEV1,65536,0,1000,ERRBUF)

def close_queues():

    DEV0RBUFFER.close()
    DEV0MBUFFER.close()
    DEV0CBUFFER.close()
    DEV1WBUFFER.close()
    DEV1RBUFFER.close()
    DEV1MBUFFER.close()
    DEV1CBUFFER.close()
    DEV0WBUFFER.close()
    DEV0ABUFFER.close()
    DEV1ABUFFER.close()

def restart_queues():

    close_queues()

    DEV0RBUFFER = multiprocessing.Queue()
    DEV0MBUFFER = multiprocessing.Queue()
    DEV0CBUFFER = multiprocessing.Queue()
    DEV1WBUFFER = multiprocessing.Queue()
    DEV1RBUFFER = multiprocessing.Queue()
    DEV1MBUFFER = multiprocessing.Queue()
    DEV1CBUFFER = multiprocessing.Queue()
    DEV0WBUFFER = multiprocessing.Queue()
    DEV0ABUFFER = multiprocessing.Queue()
    DEV1ABUFFER = multiprocessing.Queue()
    
## SCENARIOS FX
def loadConf():

    global STEG_ENGINE_IS_ON, F_NIV3_STEG, F_NIV4_STEG 
    global SRC_FILEPATH, DST_FILEPATH
    global SHAMIR_N, SHAMIR_K, SHAMIR_GFIELD, SHAMIR_MLR, O_ABSCISSE_SIZE, O_ORDONNEE_SIZE
    global MS_KEY_PERIOD, MS_TAPS
    global FLAG_STRING, FLAG_METHOD, FLAG_FREQ, REF_LETTER, O_HEADER_SIZE
    global F_NIV3, PROTO3, F_NIV3_SRC, F_NIV3_DST
    global F_NIV4, PROTO4

    # STEGOSYSTEME
    STEG_ENGINE_IS_ON = stegconf.STEG_ENGINE_IS_ON
    F_NIV3_STEG = stegconf.F_NIV3_STEG
    F_NIV4_STEG = stegconf.F_NIV4_STEG

    # APPLI
    SRC_FILEPATH = appliconf.SRC_FILEPATH
    DST_FILEPATH = appliconf.DST_FILEPATH

    # SHAMIR
    SHAMIR_ON = appliconf.SHAMIR_ON
    SHAMIR_N = appliconf.SHAMIR_N
    SHAMIR_K = appliconf.SHAMIR_K
    SHAMIR_GFIELD = appliconf.SHAMIR_GFIELD
    SHAMIR_MLR = appliconf.SHAMIR_MAX_LETTER_REF

    O_ABSCISSE_SIZE = int(math.log(SHAMIR_N,2))+1
    O_ORDONNEE_SIZE = 7 # Y modulo is SHAMIR_GFIELD, hence 67, hence 7 bits # should automatise calculus

    # MSEQUENCE
    MSEQUENCE_ON = appliconf.MSEQUENCE_ON
    MS_KEY_PERIOD = appliconf.MS_KEY_PERIOD
    MS_TAPS = appliconf.MS_TAPS

    # PROTOCOL
    FLAG_STRING = appliconf.FLAG_STRING
    FLAG_METHOD = appliconf.FLAG_METHOD
    FLAG_FREQ = appliconf.FLAG_FREQ
    REF_LETTER = appliconf.REF_LETTER
    O_HEADER_SIZE = REF_LETTER+1

    # FILTERS
    F_NIV3 = stegconf.F_NIV3
    PROTO3 = stegconf.PROTO3
    F_NIV3_SRC = stegconf.F_NIV3_SRC
    F_NIV3_DST = stegconf.F_NIV3_DST

    F_NIV4 = stegconf.F_NIV4
    PROTO4 = stegconf.PROTO4

def changeScenar(scenario_name):

    global SCENARIO_NAME
    
    fsrc = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),DEFAULT_STEGCONF)
    fdst = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),BACKUP_STEGCONF)
    shutil.copy(fsrc,fdst)
    
    fsrc = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),SCENARIO_FOLDER,STEGSCENAR_FOLDER,str(scenario_name)+".py")
    fdst = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),DEFAULT_STEGCONF)
    shutil.copy(fsrc,fdst)
    
    fsrc = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),DEFAULT_APPLICONF)
    fdst = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),BACKUP_APPLICONF)
    shutil.copy(fsrc,fdst)
    
    fsrc = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),SCENARIO_FOLDER,APPLISCENAR_FOLDER,str(scenario_name)+".py")
    fdst = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),DEFAULT_APPLICONF)
    shutil.copy(fsrc,fdst)
    
    SCENARIO_NAME = scenario_name

def checkScenar(scenario_name):
    #steg_description = importlib.import_module(os.path.join(SCENARIO_FOLDER,STEGSCENAR_FOLDER,str(scenario_name))).DESCRIPTION
    steg_description = importlib.import_module(str(SCENARIO_FOLDER)+"."+str(STEGSCENAR_FOLDER)+"."+str(scenario_name)).DESCRIPTION
    #appli_description = importlib.import_module(os.path.join(SCENARIO_FOLDER,APPLISCENAR_FOLDER,str(scenario_name))).DESCRIPTION
    appli_description = importlib.import_module(str(SCENARIO_FOLDER)+"."+str(APPLISCENAR_FOLDER)+"."+str(scenario_name)).DESCRIPTION
    return steg_description+'\n'+appli_description

#### WORKERS ####

## NET WORKERS ##

# NET PROBE
class ProbeSpider(multiprocessing.Process):

    def __init__(self,num,verbose=False):
        multiprocessing.Process.__init__(self)
        self.wtype = "engine"
        self.verbose = verbose
        self.is_running = True
        self.num = num
        if self.verbose:
            print "ProbeSpider starting"

    def run(self):
        if self.num == 0:
            handler = DEV0HANDLER
        elif self.num == 1:
            handler = DEV1HANDLER

        while self.is_running:
            hdr = ctypes.POINTER(winpcapy.pcap_pkthdr)()
            pkt = ctypes.POINTER(ctypes.c_ubyte)()
            res = winpcapy.pcap_next_ex(handler,ctypes.byref(hdr),ctypes.byref(pkt))
            if res>0:
                print "PROBE : packet found (len : "+str(hdr.contents.len)+")"
                if self.verbose:
                    data = ctypes.string_at(pkt,hdr.contents.len)
                    print "PROBE : packet content : "+str(data)+"\n"
        if self.verbose:
            print "ProbeSpider stoped"

        return

# NET WORKER (IN)
class ReadingSpider(multiprocessing.Process):

    def __init__(self,num):
        multiprocessing.Process.__init__(self)
        self.wtype = "engine"
        self.num = num
        self.otbuffer = 0
        self.inMac = 0
        self.is_running = True
        self.handler = 0
        self.x = 0 # remplacer par complement a 1 du chiffre ? (i.e. c'est l'inverse binaire de num a priori)

        if num == 0:
            self.otbuffer = DEV0RBUFFER
            self.inMac = DEV0MAC
            self.x = 1
        elif num == 1:
            self.otbuffer = DEV1RBUFFER
            self.inMac = DEV1MAC

    def run(self):
        handler = 0
        if self.num == 0:
            handler = DEV0HANDLER
        elif self.num == 1:
            handler = DEV1HANDLER

        while self.is_running:
            hdr = ctypes.POINTER(winpcapy.pcap_pkthdr)()
            pkt = ctypes.POINTER(ctypes.c_ubyte)()
            res = winpcapy.pcap_next_ex(handler,ctypes.byref(hdr),ctypes.byref(pkt))
            if res>0 :
                data = ctypes.string_at(pkt,hdr.contents.len)
                if netlib.read_mac_hdr(data)[self.x] == self.inMac: # nota bene : limite effet passerelle
                    self.otbuffer.put(data)

        return

# NET WORKER (OUT)
class WritingSpider(multiprocessing.Process):

    def __init__(self,num):
        multiprocessing.Process.__init__(self)
        self.wtype = "engine"
        self.num = num
        self.inbuffer = 0
        self.is_running = True
        self.handler = 0

        if self.num == 0:
            self.inbuffer = DEV1WBUFFER
        elif self.num == 1:
            self.inbuffer = DEV0WBUFFER

    def run(self):
        handler = 0

        if self.num == 0:
            handler = DEV1HANDLER
        elif self.num == 1:
            handler = DEV0HANDLER

        while self.is_running:
            for data in iter(self.inbuffer.get, None):
                data = netlib.format_packet(data)
                winpcapy.pcap_sendpacket(handler,data,len(data))
        return

# NET WORKER (MID)
class MiddleSpider(multiprocessing.Process):
        
    def __init__(self,num):
        multiprocessing.Process.__init__(self)
        self.wtype = "engine"
        self.num = num
        
        self.inbuffer = 0
        self.otbuffer = 0
        
        self.inMac = 0
        self.inIp = 0
        self.outMac = 0
        self.outIp = 0
        
        self.is_running = True
        self.type3 = 0

        if self.num == 0:
            self.inbuffer = DEV0MBUFFER
            self.otbuffer = DEV1WBUFFER
            self.inMac = DEV0MAC
            self.inIp = DEV0IP
            self.outMac = DEV1MAC
            self.outIp = DEV1IP
            
        elif self.num == 1:
            self.inbuffer = DEV1MBUFFER
            self.otbuffer = DEV0WBUFFER
            self.inMac = DEV1MAC
            self.inIp = DEV1IP
            self.outMac = DEV0MAC
            self.outIp = DEV0IP
            
    def run(self):
        while self.is_running:
            for data in iter(self.inbuffer.get, None):
                
                # translation d'adresses niveau 2
                if self.num == 0:
                    data = data[:6]+netlib.format_mac(self.outMac)+data[12:] # switch MAC
                elif self.num == 1:
                    data = netlib.format_mac(self.outMac)+data[6:] # switch MAC

                # translation d'adresses niveau 3 + calcul de checksums
                self.type3 = netlib.get_type3(data[12:14])
                
                if self.type3 == "0806": # si ARP
                    data = netlib.arp_rewriting(data,self.outMac,self.outIp,self.num)
                    # optimisation : si preformat lors de init, moins de taff dans netlib
                    
                elif self.type3 == "0800": # si IPv4
                    ipsrc = data[26:30]
                    ipdst = data[30:34]
                    # optimisation : passer le format_ip dans l'init
                    if self.num == 0:
                        if ipsrc == netlib.format_ip(self.inIp):
                            ipsrc = netlib.format_ip(self.outIp)
                    elif self.num == 1:
                        if ipdst == netlib.format_ip(self.inIp):
                            ipdst = netlib.format_ip(self.outIp)
                    data = netlib.ip_rewriting(data,ipsrc,ipdst) # nat + checksum
                    
                    if netlib.udp_or_tcp(data[23]): # si udp ou tcp
                        data = netlib.tcpudp_rewriting(data) # checksum niveau4
                        
                self.otbuffer.put(data)
        return 

## CRAFT WORKERS ##

# NOVICE SPIDER
# No craft functions, no craft buffer
class NoviceSpider(multiprocessing.Process):

    def __init__(self,num):
        multiprocessing.Process.__init__(self)
        self.wtype = "craft"
        self.num = num
        self.is_running = True

        self.inbuffer = 0
        self.otbuffer = 0

        if self.num == 0:
            self.inbuffer = DEV0RBUFFER
            self.otbuffer = DEV0MBUFFER
        elif self.num == 1:
            self.inbuffer = DEV1RBUFFER
            self.otbuffer = DEV1MBUFFER

    def run(self):
        while self.is_running:
            for data in iter(self.inbuffer.get, None):    
                self.otbuffer.put(data)

        return

# STEG WORKER
class StegSpider(multiprocessing.Process):

    def check_steg(self,data):

        doin = True

        if not STEG_ENGINE_IS_ON:
            doin = False

        # LEVEL 3 : PROTOCOL FILTER
        if F_NIV3 != "":
            if self.type3 != PROTO3:
                doin = False

        # LEVEL 3 : DESTINATION ADDRESS FILTER
        if F_NIV3_DST != "":
            if self.type3 == "0800":
                if not (steglib.check_ip(data[30:34],netlib.format_ip(F_NIV3_DST))): # ipv6 : 0x86dd, data[38:54]
                    doin = False
            else:
                doin = False

        # LEVEL 3 : SOURCE ADDRESS FILTER
        if F_NIV3_SRC != "":
            if self.type3 == "0800":
                if not (steglib.check_ip(data[26:30],netlib.format_ip(F_NIV3_SRC))): # ipv6 : 0x86dd, data[22:38]
                    doin = False
            else:
                doin = False

        # LEVEL 4 : PROTOCOL FILTER
        if F_NIV4 != "":
            if self.type4 != PROTO4:
                doin = False

        return doin

    # MAIN
    def __init__(self,num):
        multiprocessing.Process.__init__(self)
        self.wtype = "craft"
        self.num = num
        
        self.inbuffer = 0
        self.craftbuffer = 0
        self.otbuffer = 0
        
        self.is_running = True
        self.type3 = ""
        self.type4 = ""

        if self.num == 0:
            self.inbuffer = DEV0RBUFFER
            self.craftbuffer = DEV0CBUFFER
            self.otbuffer = DEV0MBUFFER
            
        elif self.num == 1:
            self.inbuffer = DEV1RBUFFER
            self.craftbuffer = DEV1CBUFFER
            self.otbuffer = DEV1MBUFFER
            
    def run(self):
        
        while self.is_running:
            for data in iter(self.inbuffer.get, None):

                # recognising protocols
                self.type3 = netlib.get_type3(data[12:14])
                if self.type3 == "0800": # what about ipv6 ? what about other protocols ?
                    try:
                        self.type4 = netlib.get_type4(data[23]) # get type4 for ipv4 VS get type4 for ipv6 ?
                    except Exception:
                        self.type4 = ""
                        pass

                # doin' stegano ? filtering step
                if self.check_steg(data) : # a optimiser en envoyant que les datas necessaires
                    
                    # BINPACK
                    data = steglib.binpack(data)

                    # UNPAQUET
                    paquet = [] # will contain list of dicts(name, position, size, workable, value)
                    
                    # unpacket level 2
                    header,data = packetparser.unPaquet(data,"Ethernet") # quid not Ethernet ?
                    paquet += [header]
                    
                    # unpacket level 3
                    try:
                        header,data = packetparser.unPaquet(data,{v: k for k,v in stegconf.NIV3_DICT.items()}[self.type3])
                        paquet += [header]
                    except Exception as e:
                        print "ACHTUNG ! unPaquet level 3 for "+str(self.type3)+": "+str(e)
                        pass
                    
                    # unpacket level 4
                    if self.type4 != "":
                        try:
                            header, data = packetparser.unPaquet(data,{v: k for k,v in stegconf.NIV4_DICT.items()}[self.type4])
                            paquet += [header]
                        except Exception as e:
                            print "ACHTUNG ! unPaquet level 4 for "+str(self.type4)+": "+str(e)
                            pass

                    # GET WORKABLE BITS
                    tab = [] # will contain ''.join(getWorkableBits(header)), a str(list of workable bits)
                    if F_NIV3_STEG and len(paquet)>1:
                        tab += [''.join(steglib.getWorkableBits(paquet[1]))] # manipulera un header
                    if F_NIV4_STEG and len(paquet)>2:
                        tab += [''.join(steglib.getWorkableBits(paquet[2]))] # manipulera un header
                    
                    totalen = sum([len(t) for t in tab])

                    # INSERTION / EXTRACTION
                    if totalen>6: # enough space for protocol and data ?
                        if self.num == 0 : # insertion
                            print "INSERTION START"
                            
                            # maxsize according to protocol, max 31 (3*8+7) bits plus 6 (2+3+1) bits of protocol
                            localbuff = list()
                            
                            # data waiting to be steganographied
                            newlen = min(totalen,31+6)
                            if not self.craftbuffer.empty():
                                while (len(localbuff)<(newlen-6) and not (self.craftbuffer.empty())):
                                       localbuff.append(self.craftbuffer.get())

                                S = int(len(localbuff)/8.0)
                                O = len(localbuff) - S*8

                                temptab = ''.join(tab)
                                while len(localbuff)<(totalen-6):
                                    localbuff.append(str(temptab[len(localbuff)])) # too slow ?

                                localbuff = list(bin(S)[2:].zfill(2))+list(bin(O)[2:].zfill(3))+localbuff # len+5
                                
                                localbuff.append(str(steglib.xor_complement1(map(int, localbuff)))) # ajout du flag
                                
                                # localbuff a ete charge au maximum disponible, size, offset, padding et flag inclus
                                
                            else: # no data waiting
                                localbuff = list(''.join(tab)[:-1])
                                
                                localbuff.insert(random.randint(0,len(localbuff)),str(int(not(steglib.xor_complement1(map(int,localbuff)))))) # insertion du flag

                            # SET WORKABLE BITS
                            if F_NIV3_STEG and len(paquet)>1: # implies len(tab)>0
                                paquet[1] = steglib.setWorkableBits(paquet[1],localbuff[:len(tab[0])])
                            if F_NIV4_STEG and len(paquet)>2: # implies len(tab)>1
                                paquet[2] = steglib.setWorkableBits(paquet[2],localbuff[len(tab[0]):len(tab[0])+len(tab[1])])
                            
                        elif self.num == 1 : # extraction
                            print "EXTRACTION START"
                            if steglib.xor_check(map(int,list(''.join(tab)))): # flag check
                                localbuff = list(''.join(tab)[:-1])
                                dsize = (int(''.join(localbuff[:2]),2)*8)+int(''.join(localbuff[2:5]),2) # S+O (number of bytes+offset)
                                localbuff = localbuff[5:dsize+5]
                                while len(localbuff)>0:
                                    self.craftbuffer.put(localbuff.pop(0))

                    # REPAQUET
                    bindata = packetparser.repaquet(paquet,data)

                    # BINUNPACK
                    data = steglib.binunpack(bindata)

                #print "HANDING THE PACKET OVER"
                self.otbuffer.put(data)
        return

## APPLI WORKERS ##

class SpamSpider(multiprocessing.Process):

    def __init__(self,k):
        multiprocessing.Process.__init__(self)
        self.wtype = "application"
        self.is_running = True
        self.k = k
        self.t = 0
        
        self.otbuffer = DEV0CBUFFER

    def run(self):

        while (self.is_running and self.t<self.k):
            self.otbuffer.put(str(random.randint(0,1)))
            self.t += 1
        return

class FileSpider(multiprocessing.Process):
    # /!\ WARNING : APPLICATION-LEVEL FLAG SYSTEM NOT IMPLEMENTED YET /!\

    def __init__(self,num,filename):
        multiprocessing.Process.__init__(self)
        self.wtype = "application"
        self.is_running = True
        self.num = num
        self.filename = filename

        # if SHAMIR_ON ?
        self.shamirsize = (SHAMIR_MLR-1).bit_length()+(SHAMIR_N-1).bit_length()+(SHAMIR_GFIELD-1).bit_length()
        self.shamirbuffer = []
        self.shamir_rtable = {k:{} for k in range(SHAMIR_MLR)}
        self.shamir_lastref = 0
        self.shamirmessage = []
        self.shamir_tvalue = SHAMIR_GFIELD
        self.shamir_endingchar = shamirlib.BASE64_REVERSE['MESSAGE_ENDING_CHAR']
        self.shamir_defaultval = 0
        
        if self.num == 0:
            self.craftbuffer = DEV0CBUFFER
        elif self.num == 1:
            self.craftbuffer = DEV1CBUFFER

    def run(self):
        while self.is_running:
            
            if self.num == 0: # emission
                filepath = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),"files",SRC_FILEPATH,self.filename)

                with open(filepath) as f:
                    data = f.read()
                f.close()
                    
                bdata = list()
                if SHAMIR_ON:
                    bdata = shamirlib.send_message(data,SHAMIR_K,SHAMIR_N,SHAMIR_MAX_LETTER_REF,SHAMIR_GFIELD)
                else:
                    bdata = [list(bin(ord(t))[2:].zfill(8)) for t in data]

                for x in data:
                        for y in x:
                            self.craftbuffer.put(y)
                            
            if self.num == 1: # reception
                filepath = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),"files",DST_FILEPATH,self.filename)
                newdata = ""

                if SHAMIR_ON:
                    if len(self.shamirbuffer) == self.shamirsize: # if enough bits for a shamir message
                        re = shamirlib.receive_element(map(str,self.shamirbuffer),SHAMIR_MLR,SHAMIR_N) # extract letter_ref, x and y from data
                        self.shamir_rtable[re[0]][re[1]] = re[2] # assigning value y to point x for letter letter_ref

                        if re[0] == self.shamir_lastref: # still the same letter
                            if len(self.shamir_rtable[re[0]])>SHAMIR_K: # do we have enough to try to reconstruct the original data ?
                                temp = shamirlib.reconstruction(rtable[re[0]])
                                tvalue = shamirlib.modulo_fractions(temp[0],temp[1],SHAMIR_GFIELD)
                            
                                if tvalue == self.shamir_endingchar: # this is the end, my only friend, the end
                                    msg = [x for x in self.shamirmessage if x != self.shamir_endingchar] # there should be no endingchar in shamirmessage, paranoid much ?
                                    if len(msg)>0:
                                        newdata = shamirlib.post_receiving_routine(msg,SHAMIR_GFIELD,self.shamir_defaultval)

                                # re-init (optimisation ?)
                                    self.shamirbuffer = []
                                    self.shamir_rtable = {k:{} for k in range(SHAMIR_MLR)}
                                    self.shamir_lastref = 0
                                    self.shamirmessage = []
                                    self.shamir_tvalue = SHAMIR_GFIELD
                                
                                else:
                                    if tvalue != self.shamir_tvalue:
                                        self.shamir_tvalue = tvalue # think of a better correction algorithm using previous values/K in N combinations
                                    
                        else: # oh my, we are looking at a new letter !
                            self.shamirmessage += [self.shamir_tvalue] # we add the reconstructed value to the message
                            self.shamir_rtable[self.shamir_lastref] = {}
                            self.shamir_tvalue = SHAMIR_GFIELD
                            self.shamir_lastref = re[0]

                        self.shamirbuffer = [] # empty the buffer after using the shamirsize bits
                    
                    else: # get bits from craftbuffer to shamirbuffer
                        if not self.craftbuffer.empty():
                            self.shamirbuffer.append(self.craftbuffer.get())
                else:
                    while not self.craftbuffer.empty():
                        tdata = ""
                        tdata += str(self.craftbuffer.get())
                        tdata = tdata+'0'*(8-(len(newdata)%8))
                        for k in range(len(tdata)/8):
                            newdata += chr(int(tdata[k*8:(k+1)*8],2))

                with open(filepath,'w') as f:
                    f.write(newdata)
                f.close()
                
        return

# Multiple raw_input + multiprocessing conflict. To be rewritten.
class ShamirChatSpider(multiprocessing.Process):
    # /!\ WARNING : APPLICATION-LEVEL FLAG SYSTEM NOT IMPLEMENTED YET /!\

    def __init__(self,num):
        multiprocessing.Process.__init__(self)
        self.wtype = "application"
        self.is_running = True
        self.num = num

        # if SHAMIR_ON ?
        self.shamirsize = (SHAMIR_MLR-1).bit_length()+(SHAMIR_N-1).bit_length()+(SHAMIR_GFIELD-1).bit_length()
        self.shamirbuffer = []
        self.shamir_rtable = {k:{} for k in range(SHAMIR_MLR)}
        self.shamir_lastref = 0
        self.shamirmessage = []
        self.shamir_tvalue = SHAMIR_GFIELD
        self.shamir_endingchar = shamirlib.BASE64_REVERSE['MESSAGE_ENDING_CHAR']
        self.shamir_defaultval = 0

        if self.num == 0:
            self.craftbuffer = DEV0CBUFFER
        elif self.num == 1:
            self.craftbuffer = DEV1CBUFFER

    def run(self):

        while self.is_running:
            
            if self.num == 0: # emission
                
                data = str(raw_input("\n(chat) > ")) # sanitize function needed
                # will enter in conflict with ANANSI raw_input ?
                
                if data == "EXIT":
                    self.is_running = False
                    print "\n(chat) > BYE"
                else:
                    data = shamirlib.send_message(data,
                                                  SHAMIR_K,
                                                  SHAMIR_N,
                                                  SHAMIR_MLR,
                                                  SHAMIR_GFIELD)
                    
                    for x in data:
                        for y in x:
                            self.craftbuffer.put(y)
                            
            if self.num == 1: # reception
                
                if len(self.shamirbuffer) == self.shamirsize: # if enough bits for a shamir message
                    re = shamirlib.receive_element(map(str,self.shamirbuffer),SHAMIR_MLR,SHAMIR_N) # extract letter_ref, x and y from data
                    self.shamir_rtable[re[0]][re[1]] = re[2] # assigning value y to point x for letter letter_ref

                    if re[0] == self.shamir_lastref: # still the same letter
                        if len(self.shamir_rtable[re[0]])>SHAMIR_K: # do we have enough to try to reconstruct the original data ?
                            temp = shamirlib.reconstruction(rtable[re[0]])
                            tvalue = shamirlib.modulo_fractions(temp[0],temp[1],SHAMIR_GFIELD)
                            
                            if tvalue == self.shamir_endingchar: # this is the end, my only friend, the end
                                msg = [x for x in self.shamirmessage if x != self.shamir_endingchar] # there should be no endingchar in shamirmessage, paranoid much ?
                                if len(msg)>0:
                                    print "\nMSG : "+shamirlib.post_receiving_routine(msg,SHAMIR_GFIELD,self.shamir_defaultval)

                                # re-init (optimisation ?)
                                self.shamirbuffer = []
                                self.shamir_rtable = {k:{} for k in range(SHAMIR_MLR)}
                                self.shamir_lastref = 0
                                self.shamirmessage = []
                                self.shamir_tvalue = SHAMIR_GFIELD
                                
                            else:
                                if tvalue != self.shamir_tvalue:
                                    self.shamir_tvalue = tvalue # think of a better correction algorithm using previous values/K in N combinations
                                    
                    else: # oh my, we are looking at a new letter !
                        self.shamirmessage += [self.shamir_tvalue] # we add the reconstructed value to the message
                        self.shamir_rtable[self.shamir_lastref] = {}
                        self.shamir_tvalue = SHAMIR_GFIELD
                        self.shamir_lastref = re[0]

                    self.shamirbuffer = [] # empty the buffer after using the shamirsize bits
                    
                else: # get bits from craftbuffer to shamirbuffer
                    if not self.craftbuffer.empty():
                        self.shamirbuffer.append(self.craftbuffer.get())
        return
