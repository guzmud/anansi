#!/usr/bin/env python3
"""low-level network management
"""

import netifaces


def debug_callback(pkt):
    """print the show2 packet content"""
    print(pkt.show2(dump=True))


def interface_addr2(name):
    """return the level 2 MAC"""
    return netifaces.ifaddresses(name)[17].pop(0)['addr']


def defaultgw_interface():
    """return the default gateway interface name"""
    ip, name = netifaces.gateways()['default'][2]
    return {'name': name, 'ip': ip}
