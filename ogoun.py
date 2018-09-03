#!/usr/bin/env python3
"""os-dependent functions
"""

from sys import platform

if platform.startswith('linux'):
    from baron_manchot import *
elif platform.startswith('win'):
    from baron_fenestre import *
else:  # os2, freebsd, java, cygwin, darwin, riscos, atheos
    raise NotImplementedError
