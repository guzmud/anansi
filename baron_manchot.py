#!/usr/bin/env python3

import subprocess


def tapup():
    """create the spider tap interface"""
    subprocess.run(["ip", "tuntap", "add", "mode", "tap", "dev", "spider"],
                   check=True)
    subprocess.run(["ifconfig", "spider", "up"], check=True)


def tapdown():
    """destroy the spider tap interface"""
    subprocess.run(["ifconfig", "spider", "down"], check=True)
    subprocess.run(["ip", "tuntap", "del", "mode",  "tap", "dev", "spider"],
                   check=True)
