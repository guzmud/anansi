#!/usr/bin/env python3
"""legba is the lwa of crossroads
"""

import netifaces


def debug_callback(pkt):
    """print the show2 packet content"""
    print(pkt.show2(dump=True))


def defaultgw_interface():
    """return the default gateway interface name"""
    return netifaces.gateways()['default'].popitem()[1][1]
