#! /usr/bin/python

#### LIBS ####

import ctypes

import lib_checksum as checksumlib

#### FX ####

## NIVEAU 2

def read_mac_hdr(data):
    temp = ''.join([hex(ord(i))[2:].zfill(2) for i in data[:12]])
    return temp[:12].lower(),temp[12:].lower()

def format_mac(oldmac):
    temp = ""
    for i in range(len(oldmac)/2):
        temp += chr(int(oldmac[i*2:(i+1)*2],16))
    return temp

def get_type3(data): # ethertype
    return hex(ord(data[0]))[2:].zfill(2)+hex(ord(data[1]))[2:].zfill(2)

## NIVEAU 3

def format_ip(ip): # potentiellement foireuse ?
    return ''.join([chr(int(i)) for i in str(ip).split('.')])

def ip_rewriting(data,ipsrc,ipdst):
    
    nckdata = checksumlib.checksum_ip(data[14:26]+ipsrc+ipdst)
    
    #return data[:14]+data[14:24]+nckdata+ipsrc+ipdst+data[34:]
    return data[:24]+nckdata+ipsrc+ipdst+data[34:]

def arp_rewriting(data,newMac,newIp,num):
    # default assumptions
    # hardware type : Ethernet (1), protocol type : IP (0x0800)
    # hardware size : 6, protocol size : 4
    
    if num == 0:
        macsrc = format_mac(str(newMac).lower())
        ipsrc = format_ip(str(newIp))
        macdst = data[32:38]
        ipdst = data[38:42]
        
    elif num == 1:
        macsrc = data[22:28]
        ipsrc = data[28:32]
        macdst = format_mac(str(newMac).lower())
        ipdst = format_ip(str(newIp))
    else:
        mcsrc = ""
        ipsrc = ""
        macdst = ""
        ipdst = ""

    return data[:22]+macsrc+ipsrc+macdst+ipdst

def udp_or_tcp(data):

    temp = False
    data = ord(data) #typ = hex(ord(data))[2:].zfill(2)
    if data == 6: # 0x06
        temp = True
    elif data == 17: # 0x11
        temp = True
    return temp

def get_type4(data): # to be used at the right position, probably 23th byte
    return hex(ord(data))[2:].zfill(2)

## NIVEAU 4

def tcpudp_rewriting(data):
    
    #ihl = checksumlib.find_IHL(checksumlib.stringASCII2hexarray(data))/2
    #offset = checksumlib.get_offset(checksumlib.stringASCII2hexarray(data))/2
    
    #ihl = checksumlib.find_IHL(list(data.encode("hex")))/2
    #offset = checksumlib.get_offset(list(data.encode("hex")))/2
    #hck = checksumlib.checksum_tcp(data)

    h2 = data[:14]
    data = data[14:]

    hck,ihl,offset = checksumlib.extended_checksum_tcp(data)
    pck_len = (ihl+offset)/2
    ck_len = 2

    return h2+data[:pck_len]+hck+data[pck_len+ck_len:]

    #return h2+data[:ihl+offset]+hck+data[ihl+offset+ck_len:]

## PASSAGE PYTHON/C

def format_packet(data):
    newdata = ctypes.cast(data, ctypes.POINTER(ctypes.c_ubyte * len(data)))[0]
    return newdata

#def format_ip(ip):
#    # potentiellement foireuse !
#    temp = str(ip).split('.')
#    newip =""
#    for i in range(len(temp)):
#        newip += chr(int(temp[i]))
#    return newip
