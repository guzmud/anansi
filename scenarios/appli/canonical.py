#! /usr/bin/python

DESCRIPTION = "Appli : shamir on, msequence on, flag 101010."

# FILES
SRC_FILEPATH = ""
DST_FILEPATH = ""

# SHAMIR
SHAMIR_ON = True
SHAMIR_N = 5
SHAMIR_K = 3
SHAMIR_GFIELD = 67 # prime number just above the 64 possible values of a base64 message
SHAMIR_MAX_LETTER_REF = 4

# MSEQUENCE
MSEQUENCE_ON = True
MS_KEY_PERIOD = 160
MS_TAPS = [1,2]

# PROTOCOL
FLAG_STRING = "101010"

FLAG_METHOD = 1 # going to be old very soon
FLAG_FREQ = 2 # going to be old very soon

REF_LETTER = 3 # shamir protocol, will be replaced by max_ref_letter
MS_KEY_PERIOD = 5 # going to be old very soon
