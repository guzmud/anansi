#! /usr/bin/python
# CANONICAL SCENARIO

DESCRIPTION = "Filters : level 4 ICMP, level 3 destination 8.8.8.8.\nCraft : IP."

# LEVEL 2 FILTERS
#F_NIV2 = "Ethernet" # not implemented yet

# LEVEL 3 FILTERS
NIV3_DICT = {"":"0000","IP":"0800","ARP":"0806"}
F_NIV3 = ""
PROTO3 = NIV3_DICT[F_NIV3] # a supprimer et remplacer par NIV3_DICT[F_NIV3] directement ?
F_NIV3_SRC = "" # "" is an equivalent to 0.0.0.0 that will automatically bypass
F_NIV3_DST = "8.8.8.8"

# F_NIV3_STATE

# LEVEL 4 FILTERS

NIV4_DICT = {"":"00","ICMP":"01","TCP":"06","UDP":"11"}
F_NIV4 = "ICMP" 
PROTO4 = NIV4_DICT[F_NIV4]
F_NIV4_SRC = ""
F_NIV4_DST = ""

# F_NIV4_STATE

# LEVEL 5 FILTERS

# F_NIV5_STATE, F_NIV5

# STEGOSYSTEME

STEG_ENGINE_IS_ON = True
F_NIV3_STEG = True
F_NIV4_STEG = False
