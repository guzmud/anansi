#! /usr/bin/python
# some code stolen from examples in winpcapy
# IPv4-oriented, IPv6 todo
# best-effort algorithms

## LIBS

import ctypes, subprocess, re, os, inspect

import winpcapy

## GLOBALS

GATEWAY = ""
OSTYPE = ""

## CLASSES

class ifdev():
    num = ""
    dsp = ""
    path = ""
    mac = ""
    ip = ""
    mask = ""
    name = "" # windows only ?
    wnum = "" # windows only ?

RDEV = ifdev()
VDEV = ifdev()
TDEV = ifdev()

# stolen from winpcapy examples

class S_un_b(ctypes.Structure):
    _fields_ = [("s_b1",ctypes.c_ubyte),
                ("s_b2",ctypes.c_ubyte),
                ("s_b3",ctypes.c_ubyte),
                ("s_b4",ctypes.c_ubyte)]

class S_un_w(ctypes.Structure):
    _fields_ = [("s_wl",ctypes.c_ushort),
                ("s_w2",ctypes.c_ushort)]

class S_un(ctypes.Union):
    _fields_ = [("S_un_b",S_un_b),
                ("S_un_w",S_un_w),
                ("S_addr",ctypes.c_ulong)]

class in_addr(ctypes.Structure):
    _fields_ = [("S_un",S_un)]

class sockaddr_in(ctypes.Structure):
    _fields_ = [("sin_family", ctypes.c_ushort),
                ("sin_port", ctypes.c_ushort),
                ("sin_addr", in_addr),
                ("sin_zero", ctypes.c_char * 8)]

## FX

def cast2str(a):
    a = a.contents.sin_addr.S_un.S_un_b
    return str(a.s_b1)+"."+str(a.s_b2)+"."+str(a.s_b3)+"."+str(a.s_b4)

def ip_plus_one(ip):
    temp = ip.split(".")
    if int(temp[-1]) > 250:
        temp[-1] = str(int(temp[-1])-1)
    else:
        temp[-1] = str(int(temp[-1])+1)
    return '.'.join(temp)

## FX (GET)

def get_pcapinfo(devnum):
    temp1 = []
    temp2 = []
    alldevs=ctypes.POINTER(winpcapy.pcap_if_t)()
    errbuf= winpcapy.create_string_buffer(winpcapy.PCAP_ERRBUF_SIZE)
    
    if (winpcapy.pcap_findalldevs(ctypes.byref(alldevs), errbuf) == -1):
        print ("Error in pcap_findalldevs: %s\n" % errbuf.value)
        sys.exit(1)

    i=0
    try:
        d=alldevs.contents
    except:
        print ("Error in pcap_findalldevs: %s" % errbuf.value)
        sys.exit(1)

    for i in range(0,devnum):
        d=d.next.contents

    if d.name:
        temp1 += [d.name]
    if d.description:
        temp1 += [d.description]
    
    if d.addresses:
        a=d.addresses.contents
    else:
        a=False
    while a:
        a_temp = []
        if a.addr:
            a_temp += [cast2str(ctypes.cast(a.addr,ctypes.POINTER(sockaddr_in)))]
        else:
            a_temp += [404]
            
        if a.netmask:
            a_temp += [cast2str(ctypes.cast(a.netmask,ctypes.POINTER(sockaddr_in)))]
        else:
            a_temp += [404]

        temp2 += [a_temp,]
                       
        if a.next:
            a=a.next.contents
        else:
            a=False

    #try:
    #    winpcap.pcap_freealldevs(alldevs)
    #except:
    #    print ("Error in pcap_freealldevs")

    return temp1, temp2

def get_devlist():
    temp = []
    alldevs=ctypes.POINTER(winpcapy.pcap_if_t)()
    errbuf= winpcapy.create_string_buffer(winpcapy.PCAP_ERRBUF_SIZE)
    
    if (winpcapy.pcap_findalldevs(ctypes.byref(alldevs), errbuf) == -1):
        print ("Error in pcap_findalldevs: %s\n" % errbuf.value)
        sys.exit(1)

    i=0
    try:
        d=alldevs.contents
    except:
        print ("Error in pcap_findalldevs: %s" % errbuf.value)
        sys.exit(1)

    while d:
        temp += [str(d.name)]
        i += 1
        if d.next:
            d=d.next.contents
        else:
            d=False

    if (i==0):
        print ("\nNo interfaces found! Make sure WinPcap is installed.\n")
        sys.exit(-1)

    #try:
    #    winpcap.pcap_freealldevs(alldevs)
    #except:
    #    print ("Error in pcap_freealldevs")

    return temp

## FX (SUBPROCESS)

def get_intname(tpath):
    temp = ""

    if OSTYPE.lower() == "dos":
        import _winreg
        path = 'SYSTEM\\CurrentControlSet\\Control\\Network\\{4D36E972-E325-11CE-BFC1-08002BE10318}'
        tpath = tpath.split("NPF_")[1]
        fullpath = path+"\\"+tpath+"\\"+'Connection'

        key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, fullpath, 0, _winreg.KEY_ALL_ACCESS)
        temp = str(_winreg.QueryValueEx(key, 'Name')[0].encode('ascii','replace'))
        
    elif OSTYPE.lower() == "linux":
        print "not implemented yet"
        
    else:
        print "OS type unknown"
        
    return temp

# algo a ameliorer (crude hack)
def get_gateway():
    global GATEWAY
    temp = ""
    
    if RDEV.ip != "":
        if OSTYPE.lower() == "dos":
            nlist = subprocess.check_output("netsh interface ip show address").split("\r\n\r\n")
            
            found = []
            for i in nlist:
                if RDEV.ip in i:
                    found += [i]
            if len(found)>1:
                print "Too many findings. Keeping the first one (problems ahead, maybe)."
            found = found[0].split("\r\n")

            tfound = []
            for i in found:
                if ':' in i:
                    tfound += [i.split(":")[1]]
            tfound = tfound[1:]
            
            found = []
            for i in range(len(tfound)):
                if "." in tfound[i]:
                    found += [re.sub('[^0-9.]+','',tfound[i])]

            if len(found)>2:
                temp = found[2]
            else:
                print "Couldn't determine the IP address of the gateway"
                
        elif ostype.lower() == "linux":
            print "not implemented yet"
            
        else:
            print "OS type unknown"
    else:
        print "RDEV.ip not set"

    if temp != "":
        GATEWAY = temp

def setvdev():

    ipv4 = ""
    mask = ""
    gw = ""
    
    if str(raw_input("Confirm device "+str(VDEV.num)+" is the virtual device [y/n]\n> ")).lower() == 'y':

        # IP
        print RDEV.ip+" is the real device's IP."
        if str(raw_input("Is "+str(ip_plus_one(RDEV.ip))+" okay as virtual device's IP ? [y/n]\n> ")).lower() == 'y':
            ipv4 = str(ip_plus_one(RDEV.ip))
        else:
            ipv4 = str(raw_input("Please enter the virtual device's IP [1.2.3.4]\n> "))

        ## MASK
        if str(raw_input("Is "+str(RDEV.mask)+" okay as virtual device's mask ? [y/n]\n> ")).lower() == 'y':
            mask = str(RDEV.mask)
        else:
            mask = str(raw_input("Please enter the virtual device's mask [1.2.3.4]\n> "))

        ## GATEWAY
        if GATEWAY == "":
            get_gateway()
        if str(raw_input("Is "+str(GATEWAY)+" okay as gateway's IP ? [y/n]\n> ")).lower() == 'y':
            gw = str(GATEWAY)
        else:
            gw = str(raw_input("Please enter the gateway's IP [1.2.3.4]\n> "))

        ## LOAD'N'LOCK
        print "VIRTUAL DEVICE IP CONFIGURATION"
        print "IPv4 : "+str(ipv4)
        print "MASK : "+str(mask)
        print "GATEWAY : "+str(gw)
        if str(raw_input("Confirm and set configuration [y/n]\n> ")).lower() == 'y':
            wnum = VDEV.wnum
            print "DOS name of the interface : "+str(VDEV.name)+", interface DOS id : "+str(VDEV.wnum)
            if str(raw_input("Confirm device [y/n]\n> ")).lower() == 'y':
                subprocess.call('netsh interface ip set address name="'+str(wnum)+'" static '+str(ipv4)+' '+str(mask)+' '+str(gw))
            refresh_devvar(ipv4,mask)
            print "Done, sir"

def get_macaddress(intname):
    temp = ""

    if OSTYPE.lower() == "dos":
        nlist = [filter(None,x.split("\r\n")) for x in subprocess.check_output("getmac /V /FO list").split("\r\n\r\n")]
        for l in nlist:
            if l[0].split(":")[1].strip().lower() == intname.lower():
                temp = ''.join(l[2].split(":")[1].strip().split('-')).lower()
        if temp == "":
            print "No MAC found for this interface !"
        
    elif OSTYPE.lower() == "linux":
        print "Not implemented yet"
    else:
        print "OS type unknown"
    
    return temp

def get_nicnum(nic_mac):
    temp = 0
    if OSTYPE.lower() == "dos":
        nlist = subprocess.check_output("route print")
        found = []
        for i in nlist.split("\r\n"):
            if nic_mac in i.replace(' ',''):
                found += [i.replace(' ','')]
        temp = int(found[0].split('.')[0])
                
    elif OSTYPE.lower() == "linux":
        print "not implemented yet"
            
    else:
        print "OS type unknown"
        
    return temp   

def set_route(nic_wnum,gtw_ip):
    
    print "Interface "+str(nic_wnum)+" to "+str(gtw_ip)
    if str(raw_input("Confirm ? [y/n]\n> ")).lower() == 'y':
        if OSTYPE.lower() == "dos":
            subprocess.call("route delete 0.0.0.0")
            subprocess.call("route add 0.0.0.0 mask 0.0.0.0 "+str(gtw_ip)+" if "+str(nic_wnum))
                
        elif OSTYPE.lower() == "linux":
            print "not implemented yet"
        
        else:
            print "OS type unknown"

## FX (FILE)
        
def gen_netconf():
    
    print 'DEVICE1 = "'+str(VDEV.path)+'"'
    print 'DEV1MAC = "'+str(VDEV.mac)+'"'
    print 'DEV1IP = "'+str(VDEV.ip)+'"'
    print ""
    print 'DEVICE2 = "'+str(RDEV.path)+'"'
    print 'DEV2MAC = "'+str(RDEV.mac)+'"'
    print 'DEV2IP = "'+str(RDEV.ip)+'"'
    
    if str(raw_input("Confirm ? [y/n]\n> ")).lower() == 'y':
        data = '#! /usr/bin/python\n'
        data += '# generated with papa legba\n\n'
        data += 'DEVICE1 = "'+str(VDEV.path)+'"\nDEV1MAC = "'+str(VDEV.mac)+'"\nDEV1IP = "'+str(VDEV.ip)+'"\n\n'
        data += 'DEVICE2 = "'+str(RDEV.path)+'"\nDEV2MAC = "'+str(RDEV.mac)+'"\nDEV2IP = "'+str(RDEV.ip)+'"\n'
        with open(os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),'conf_net.py'),"w") as text_file:
            text_file.write(data)
        text_file.close()
        print "conf_net.py written"

## FX (VARS)

def refresh_devvar(newip,newmask):

    global VDEV
    
    devinfo, deviplist = get_pcapinfo(VDEV.num)
    VDEV.path = devinfo[0]
    for i in deviplist:
        if i[0]==newip:
            VDEV.ip = i[0]
            VDEV.mask = i[1]
    # remontee d'erreur si aucun i[0]==newip ?

## FX (MENU)

def route_menu():
    if GATEWAY != "":
        choice = str(raw_input("Route to real [r] ou virtual [v] device ?\n> ")).lower()
        if choice == 'r':
            if RDEV.ip != "" :
                set_route(RDEV.wnum,GATEWAY)
            else:
                print "Please, get RDEV_IP first."
        elif choice == 'v':
            if VDEV.ip != "" :
                set_route(VDEV.wnum,GATEWAY)
            else:
                print "Please, get VDEV_IP first."
        else:
            print "Sorry, I could not understand your choice ("+str(choice)+")"
    else:
        print "Please, get gateway ip address first."

def devlist_menu():
    devlist = get_devlist()
    print "\tLEGBA : Devices list"
    for i in range(len(devlist)):
        print "\t"+str(i)+" : "+str(devlist[i])

def print_device(dtype):

    xdev = ""

    if dtype == "rdev":
        xdev = RDEV
    elif dtype == "vdev":
        xdev = VDEV
    elif dtype == "tdev":
        xdev = TDEV

    print "DEV : "+str(xdev.num)+" : "+str(xdev.dsp)+" : "+str(xdev.path)
    print "NIC : "+str(xdev.wnum)+" : "+str(xdev.name)+" : "+str(xdev.mac)+" : "+str(xdev.ip)+" : "+str(xdev.mask)

def devchoice_menu(dtype):
    
    global RDEV, VDEV, TDEV

    xdev = ""
    if dtype == "rdev":
        xdev = RDEV
    elif dtype == "vdev":
        xdev = VDEV
    elif dtype == "tdev":
        xdev = TDEV
    
    dev_choice = int(raw_input("\tLEGBA : Device num\n> "))
    devinfo, deviplist = get_pcapinfo(dev_choice)
    print devinfo

    xdev.num = dev_choice
    xdev.dsp = devinfo[1]
    xdev.path = devinfo[0]
    print (xdev.num, xdev.dsp, xdev.path)
    
    xdev.name = get_intname(xdev.path)
    if xdev.name != "":
        xdev.mac = get_macaddress(xdev.name)
    else:
        xdev.mac = ""
    if xdev.mac != "":
        xdev.wnum = get_nicnum(xdev.mac)
    else:
        xdev.wnum = ""
    print (xdev.name, xdev.mac, xdev.wnum)
    
    temp = ""
    for i in range(len(deviplist)):
        temp += "["+str(i)+"] "+str(deviplist[i])+" ; "
    print temp
    ip_choice = int(raw_input("\tLEGBA : Please, choose main ip configuration\n> "))

    xdev.ip = deviplist[ip_choice][0]
    xdev.mask = deviplist[ip_choice][1]

def devcheck_menu():
    devchoice_menu("tdev")
    print_device("tdev")

def header():
    print "################################"
    print "\tPAPA LEGBA\n"
    print "OSTYPE : \t"+OSTYPE
    print "GATEWAY : \t"+str(GATEWAY)
    print ""
    print "REAL DEVICE"
    print_device("rdev")
    print ""
    print "VIRTUAL DEVICE"
    print_device("vdev")

## CODE

print "################################"
print "\tPAPA LEGBA\n"
print ""
OSTYPE = raw_input("LEGBA : ostype ? [dos] or [linux]\n> ")
print "LEGBA : ostype is "+str(OSTYPE)

a = ""
while a != '0':
    header()
    print ""
    print "0. Leave"
    print "1. Get devices list"
    print "2. Check device information"
    print "3. Choose real device"
    print "4. Choose virtual device"
    print "5. Find gateway address"
    print "6. Set virtual device ip configuration"
    print "7. Generate net.conf file"
    print "8. Set routes"
    print ""
    a = str(raw_input("Choice\n> "))

    if a == '1':
        devlist_menu() # fournit une liste numerotee des devices via NPF
        print ""
    elif a == '2':
        devcheck_menu() # utilise le numero de la liste precedente pour remplir TDEV
        print ""
    elif a == '3':
        devchoice_menu("rdev") # set RDEV_* a l'interface designee
        print ""
    elif a == '4':
        devchoice_menu("vdev") # set VDEV_* a l'interface designee
        print ""
    elif a == '5':
        get_gateway() # obtient l'adresse de la passerelle a partir de RDEV_IP
        print ""
    elif a == '6':
        setvdev() # configure localement l'interface virtuelle via console OS
        print ""
    elif a == '7':
        gen_netconf() # genere le fichier netconf a partir de RDEV et VDEV
        print ""
    elif a == '8':
        route_menu() # modifie le routage par defaut vers RDEV ou VDEV
print "Leaving Papa Legba ..."
