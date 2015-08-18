#! /usr/bin/python
# CANONICAL SCENARIO

DESCRIPTION = "Filters : level 3 IP.\nSteg : IP"

# LEVEL 2 FILTERS
#F_NIV2 = "Ethernet" # not implemented yet

# LEVEL 3 FILTERS
NIV3_DICT = {"":"00","IP":"0800","ARP":"0806"}
F_NIV3 = "IP"
PROTO3 = NIV3_DICT[F_NIV3]# a supprimer et remplacer par NIV3_DICT[F_NIV3] directement ?
F_NIV3_SRC = ""
F_NIV3_DST = ""

# LEVEL 4 FILTERS
NIV4_DICT = {"":"00","ICMP":"01","TCP":"06","UDP":"11"}
F_NIV4 = "" 
PROTO4 = NIV4_DICT[F_NIV4]
F_NIV4_SRC = ""
F_NIV4_DST = ""

# STEGOSYSTEME
STEG_ENGINE_IS_ON = True
F_NIV3_STEG = True
F_NIV4_STEG = False
