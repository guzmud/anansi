#-*-coding:Utf-8 -*

# WORK IN PROGRESS #

import timeit, random

## UTL

def xor(x,y):
    if isinstance(x,list) and isinstance(y,list):
        while abs(len(x)-len(y)) > 0:
            if len(x)>len(y):
                y=[0]+y 
            else:
                x=[0]+x
            
        xorList=[0] * len(x)
        for i in range(len(x)):
            xorList[i]=int(x[i])^int(y[i])
        return xorList
    else:
        return x^y

## STATELESS

# choisir l'un des deux lfsr
def lfsr(seed, taps):
    sr = seed
    nbits = seed.bit_length()
    while True:
        txor = 1
        for t in taps:
            if (sr & (1<<(t-1))) != 0:
                txor ^= 1
        sr = (txor << nbits-1) + (sr >> 1)
        yield txor, sr

#cyclique si masK > seed
def lfsr2(seed, mask):
    result = seed
    nbits = mask.bit_length()-1
    while True:
        result = (result << 1)
        txor = result >> nbits
        if txor != 0:
            result ^= mask
        yield txor, result

# [0] => nb Bits
# [1] => nb Ones
# [2] => nb Zeros
def bitLenCount(int_type):
    length = 0
    ones = 0
    while (int_type):
        ones += (int_type & 1)
        length += 1
        int_type >>= 1
    zeros = length - ones
    return(length, ones, zeros)

## METAFUNCTIONS

# modif i/o : registre_cipher, registre_decipher
def initiateurRegistre(size,registre_cipher, registre_decipher):
    initVect,registre_cipher=startSenderSession(size,registre_cipher) # registre_cipher (i/o)
    registre_decipher=startReceiverSession(initVect,registre_decipher) # registre_decipher (i/o)

    return initVect,registre_cipher,registre_decipher

# modif i/o : registre_cipher,registre_decipher # old ? / debug ?
def tester(msg,initVect,registre_cipher,registre_decipher):
    cipherMsg,registre_cipher=ciphering(msg,initVect,registre_cipher) # registre_cipher (i/o)
    msgClair,registre_decipher=deciphering(cipherMsg,initVect,registre_decipher) # registre_decipher(i/o)

    if (msg == msgClair):
        print "ok"
    else: 
        print "erreur: decode en",
        print msgClair
    return msgClair,registre_cipher,registre_decipher

## STATEFULL

#permet de reperer une periode dans un registre deja genere
# REGISTRE_CIPHER => registre_cipher
def toirtoise_and_hare(initVect,registre_cipher): # ajout de la variable registre_cipher
    tic = timeit.default_timer()
    steps = 0
    tab = []
    
    while True:
        try:
            hare = next(registre_cipher[initVect])[1]
            tab += [hare]
            hare = next(registre_cipher[initVect])[1]
            tab += [hare]
            tortoise = tab[steps]
            steps +=1
            if hare == tortoise:
                toc = timeit.default_timer()
                spent_time = toc-tic
                return steps
        except:
            break # obsolete ?
    return registre_cipher # return registre_cipher # dafuq ?

#genere un LFSR (vecteur d'initialisation aleatoire et taps)
#genere un registre depuis ce LFSR
#renvoie le vecteur d'initialisation qui servira de clef pour indexer le registre

# REGISTRE_CIPHER => registre_cipher
def startSenderSession(size,registre_cipher,taps=[2,1],test=False): # ajout de registre_cipher

    #genere un nouveau vecteur d'initialisation de la taille des briques a chiffrer
    initVect = 1<<(size-1) ^ random.randint(0, 2**(size-2))
    initVect = long(initVect)
    
    #genere le registre correspondant et le place en memoire
    registre_cipher[initVect] = lfsr(initVect,taps)
    
    if test:
        return toirtoise_and_hare(initVect)

    return initVect,registre_cipher # return registre_cipher

# REGISTRE_DECIPHER => registre_decipher
def startReceiverSession(initVect,registre_decipher,taps=[2,1]):
    size = initVect.bit_length()
    registre_decipher[initVect] = lfsr(initVect, taps)
    return registre_decipher # return registre_decipher

# REGISTRE_CIPHER => registre_cipher
#le sessionID correspond au vecteur d'initialisation utilise pour generer le registre
def ciphering(msg, initVect,registre_cipher):
    try:
        vect = next(registre_cipher[initVect])[1]
    except:
        list(registre_cipher[initVect])[1] # IndexError: list index out of range
    msg=xor(vect,msg)       
    return msg, registre_cipher # return registre_cipher

# REGISTRE_DECIPHER => registre_decipher
def deciphering(msg,initVect,registre_decipher):
    try:
        vect = next(registre_decipher[initVect])[1]
    except:
        list(registre_decipher[initVect])[1]
        msg=xor(vect,msg)
        return msg, registre_decipher # registre_decipher
