# !/usr/bin/python

# lib_net import : checksum_ip, extended_checksum_tcp

## MATHS

def carry_addition(data,n):
    ndata = ['0']*(n-len(data)%n)+list(data)
    
    # considerons pas plus de 2 elements de taille n
    # cependant un tableau de len(data)/n cases
    # for i in range(len(ndata)/n):
    #    temp += int(''.join(ndata[i*n:(i+1)*n]),16)
    
    temp = int(''.join(ndata[0:n]),16)+int(''.join(ndata[n:2*n]),16)
    return temp

# checksum ip test data : 4500003c1c4640004006b1e6ac100a63ac100a0c => b1e6
# checksum ip test data : 45000073000040004011b861c0a80001c0a800c7 => b861
def checksum_fx(data, checksum_ps=20):

    # /!\ WARNING : test default checksum value (20 if IP, more if TCP)
    # offset dans le cas du tcp/udp
    #if offset==0:
    #    checksum_ps = 20 # why not : fusionner offset et checksum_ps et une val a defaut de 20
    #else:
    #    checksum_ps = offset
    
    checksum_lg = 4

    # need padding ?
    if (len(data)%4)!=0: # ex-need_padding
        data = data+['0']*(len(data)%4)

    # on remplace le checksum
    hdr = data[:checksum_ps]+['0']*checksum_lg+data[checksum_ps+checksum_lg:]

    # on regroupe les hexa par deux, pour passer sur du 16 bits, et on somme
    u = 0
    for i in range(len(hdr)/4):
        u += int(''.join(hdr[i*4:(i+1)*4]),16)

    # carry si besoin
    newcode = hex(u)[2:].zfill(checksum_lg)
    if len(newcode)>checksum_lg: # should we loop ?
        newcode = hex(carry_addition(newcode,checksum_lg))[2:].zfill(checksum_lg)

    # on relit chaque element en binaire, on le complemente a un, et on recupere les chr
    
    c = ''.join([str(int(i)^1) for i in bin(int(newcode,16))[2:].zfill(len(newcode)*4)])
    
    k = ""
    for i in range(len(c)/8):
        k += chr(int(c[i*8:(i+1)*8],2))

    return k

## PARSER

# return IP header length
def find_IHL(data):
    return int(data[1],16)*8

# return the offset before the checksum in the header (check protocol if tcp or udp)
def get_offset(data):
    # TCP = 0x06 => 32, UDP = 0x11 => 12
    temp = 0
    proto = ''.join(data[18:20])
    if proto == "06":
        temp = 32
    elif proto == "11":
        temp = 12
    return temp

# return source ip and destination ip
def getIPs(data):
    tlen = len(data)
    ipsrc = data[tlen-16:tlen-8]
    ipdst = data[tlen-8:]
    return ipsrc,ipdst

## MAIN FUNCTIONS

# return ip pseudo-header for tcp/udp checksum
def pseudoheader_ip(data):
    IHL = find_IHL(data)
    TSL = int(''.join(data[4:8]),16)-(IHL/2) # TCP segment length : total length minus ip header length
    #TSL = (find_TL(data)-IHL)/2
    length = hex(TSL)[2:].zfill(4)
    
    ipsrc, ipdst = getIPs(data[:IHL])
    proto = "00"+''.join(data[18:20])
    #proto = "00"+(hex(int(find_proto(data[:IHL])))[2:].zfill(2))
    
    return ipsrc+ipdst+list(proto)+list(length)

# return the checksum ip
def checksum_ip(data):
    #data_ip = list(data.encode("hex")) #data_ip = stringASCII2hexarray(data)
    #return checksum_fx(data_ip)
    return checksum_fx(list(data.encode("hex")))

# return the checksum tcp/udp
def checksum_tcp(data):
    datadns = list(data.encode("hex")) # datadns = stringASCII2hexarray(data)
    psi = pseudoheader_ip(datadns)
    return checksum_fx(psi+datadns[find_IHL(datadns):],get_offset(datadns)+len(psi))

# return the checksum tcp/udp plus ihl and offset values
def extended_checksum_tcp(data):
    datadns = list(data.encode("hex"))
    ihl = find_IHL(datadns)
    offset = get_offset(datadns)
    psi = pseudoheader_ip(datadns)
    return checksum_fx(psi+datadns[ihl:],offset+len(psi)),ihl,offset
