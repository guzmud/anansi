#! /usr/bin/python
# redundancy without repetition

import fractions, random, base64, itertools

#import conf_appli as appliconf # useless ... for now ?

REF_LETTER = 0

# BASE64 TABLES
BASE64_INDEX = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G',
                7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M',
                13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S',
                19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y',
                25: 'Z', 26: 'a', 27: 'b', 28: 'c', 29: 'd', 30: 'e',
                31: 'f', 32: 'g', 33: 'h', 34: 'i', 35: 'j', 36: 'k',
                37: 'l', 38: 'm', 39: 'n', 40: 'o', 41: 'p', 42: 'q',
                43: 'r', 44: 's', 45: 't', 46: 'u', 47: 'v', 48: 'w',
                49: 'x', 50: 'y', 51: 'z', 52: '0', 53: '1', 54: '2',
                55: '3', 56: '4', 57: '5', 58: '6', 59: '7', 60: '8',
                61: '9', 62: '+', 63: '/', 64: '=', 65: 'MESSAGE_ENDING_CHAR'}

BASE64_REVERSE = dict([[v,k] for k,v in BASE64_INDEX.items()])

# MODULO FRACTIONS
def euclideEtendu(a, b):
    x,y,u,v =0,1,1,0
    while a!= 0:
        q = b//a
        r = b%a
        m = x-u*q
        n = y-v*q
        b,a,x,y,u,v = a,r,u,v,m,n
    return b,x,y

def get_invA(a, m):
    invA = 0
    if (fractions.gcd(a,m) == 1):
        g, x, y = euclideEtendu(a,m)
        invA = x%m
    return invA

def modulo_fractions(num,den,modulo):
    den = get_invA(den,modulo)
    return (num*den)%modulo

# FRACTIONS
def simple_fractions(num,den):
    k = fractions.gcd(num,den)
    num = num/k
    den = den/k
    return (num,den)

def hardcore_fractions(tfracts):
    tA = []
    tB = []
    for k in tfracts:
        tA += [k[0]]
        tB += [k[1]]

    num = 0
    den = 1
    for i in range(len(tfracts)):
        tnum = tA[i]
        for y in range(len(tfracts)):
            if y != i:
                tnum *= tB[y]
                tnum = tnum
        num += tnum
        den *= tB[i]
    return (num,den)

# SENDING MESSAGES
def gen_random_values(K,gfield):
    values = []
    for i in range(K-1): # K-1 for x**0 is s0
        values += [random.randint(1,gfield-1)]
    return values

def poly_calc(Y,X,rvalues):
    for i in range(len(rvalues)):
        Y += (rvalues[i]*pow(X,(i+1)))
    return Y #%GFIELD

def create_shares(Y,rvalues,N,gfield):
    shares = {}
    for i in range(N):
        shares[i+1] = poly_calc(Y,i+1,rvalues)%gfield
    return shares

# for each base64 element in the message, K random values are produced, N shares are created, a dictionnary is added to the array
def sending_routine(msg,K,N,gfield):

    karray = []
    array = [BASE64_REVERSE[i] for i in base64.b64encode(msg)]
    array += [65,65] # adding the special ending char post-b64 encoding, twice
    
    for i in array:
        rvalues = gen_random_values(K,gfield) # the size will determined the polynome degree, hence the minimal number of elements
        shares = create_shares(i,rvalues,N,gfield) # should we randomize the order of the shares ? warning dictionnary
        karray += [shares]

    return karray

def send_message(msg,K,N,MLR,gfield):
    global REF_LETTER

    paquets_list = []

    msg = sending_routine(msg,K,N,gfield)

    for p in msg:
        for x in p:
            refval = bin(REF_LETTER)[2:].zfill((MLR-1).bit_length()) # put ref_letter value, size MLR-1 bitsize
            xval = bin(x)[2:].zfill((N-1).bit_length()) # put x, size N-1 bitsize
            yval = bin(p[x])[2:].zfill((gfield-1).bit_length()) # put y, size GFIELD-1 bitsize
            paquet = list(refval+xval+yval)
            paquets_list.append(paquet)
        REF_LETTER = (REF_LETTER+1)%MLR
            
    return paquets_list

# RECEIVING MESSAGES
def LSF_calc(shares,nb):
    num = 1
    den = 1
    for i in shares:
        if i != nb:
            num *= (-i)
            den *= (nb-i)
    num = (num)
    den = (den)
    return (num,den)

def receive_element(share,MLR,N):
    share = ''.join(share)
    reflet = int(share[:(MLR-1).bit_length()],2)
    x = int(share[(MLR-1).bit_length():(MLR-1).bit_length()+(N-1).bit_length()],2)
    y = int(share[(MLR-1).bit_length()+(N-1).bit_length():],2)
    return (reflet,x,y)

def reconstruction(shares):
    snum = 0
    sden = 1
    tfracts = []
    for i in shares:

        num,den = LSF_calc(shares,i)        
        num,den = simple_fractions(num,den)
        
        num = (num*shares[i])
        num,den = simple_fractions(num,den)

        tfracts += [[num,den],]

    hfract = hardcore_fractions(tfracts)
    return hfract

def post_receiving_routine(ori,splitvalue,default):
    
    msg = ""
    print ori
    postmsg = " ("+str(ori.count(splitvalue))+" corrupted chars"
    
    mlist = []
    tlist = []
    for x in ori:
        if x == splitvalue:
            mlist += [tlist]
            tlist = []
        else:
            tlist += [x]
    mlist += [tlist]
    
    for i in range(len(mlist)-1):
        mlist[i] = mlist[i]+[default]
        
    count = sum([k.count(64) for k in mlist])
    ty = sum([len(t) for t in mlist])
    flow = ((ty-count)*6)%8
    miss = flow-(count*2)

    if miss == 0:
        postmsg += ", no missing char"
        
    if miss == 2:
        while len(mlist)<2: # a retravailler
            b = random.randint(1,len(mlist[0]))
            mlist = [mlist[0][:b]]+[mlist[0][b:]]
        mlist.insert(random.randint(1,len(mlist)-1),[default])
        postmsg += ", one missing char"

    if miss == 4:
        while len(mlist)<3: # a retravailler
            b = random.randint(1,len(mlist[0]))
            mlist = [mlist[0][:b]]+[mlist[0][b:]]+mlist[0:]
        mlist.insert(random.randint(1,len(mlist)-1),[default])
        mlist.insert(random.randint(1,len(mlist)-1),[default])
        postmsg += ", two missing chars"

    if miss == 6:
        while len(mlist)<4: # a retravailler
            b = random.randint(1,len(mlist[0]))
            mlist = [mlist[0][:b]]+[mlist[0][b:]]+mlist[0:]
        mlist.insert(random.randint(1,len(mlist)-1),[default])
        mlist.insert(random.randint(1,len(mlist)-1),[default])
        mlist.insert(random.randint(1,len(mlist)-1),[default])
        postmsg += ", three missing chars"

    postmsg += ")"

    try:
        msg = base64.b64decode(''.join([BASE64_INDEX[i] for i in list(itertools.chain.from_iterable(mlist))]))
        msg += postmsg
    except TypeError:
        msg = "MISSINGNO."
    return msg
