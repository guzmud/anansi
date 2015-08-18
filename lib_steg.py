#! /usr/bin/python

# find the "workable" bits in a header
def getWorkableBits(header):
    workableBits = []
    for field in header: # verifier/enforcer l'ordre numerique des fields ?
        if field["workable"]:
            workableBits += [field["value"]]
    return workableBits

# change the "workable" bits in a header
def setWorkableBits(header, newBits):
    newBits = ''.join(map(str,list(newBits)))
    for field in header: # verifier/enforcer l'ordre numerique des fields ?
        if field["workable"]:
            field["value"] = newBits[:field["size"]]
            newBits = newBits[field["size"]:]
    return header

# packet data to binary representation
def binpack(data):
    temp = ""
    for i in data:
        temp += bin(ord(i))[2:].zfill(8)
    return temp

# binary representation to packet data
def binunpack(data):
    temp = ""
    for i in range(len(data)/8):
        temp += chr(int(data[i*8:(i+1)*8],2))
    return temp

# flag
def xor_complement1(tlist):
    return int(not reduce(lambda a,b:a^b, tlist, 0))

# flag checking
def xor_check(tlist):
    return reduce(lambda a,b:a^b, tlist, 0)

# checking temporary ip against filter ip
def check_ip(tip,fip):
    doin = True
    for i in range(4):
        if ((ord(fip[i]) != 0) and (tip[i] != fip[i])):
            doin = False
    return doin
