Anansi
======

Intro
-----

**Anansi** is a network steganography system, meant to become a versatile and open network manipulation framework. The synergy between three different levels of workers (nicknamed spiders), categorized between *net* (low-level network manipulation), *craft* (essential data manipulation) and *application* (data generation), allows for various adaptation and re-use of the original work, even beyond steganography.

Using a virtual interface to route the network data into the engine, it creates a hidden channel inside legitimate channels. This channel can be used as a support for homebrew applications. The aim of the project is to produce a versatile and adaptive framework for network data manipulation, and especially network steganography.

**Legba** is a network configuration assistant, providing less-experimented users a helpful hand in order to manage the unorthodox network system needed for data flow manipulation. Through a small CLI script and a few steps (that needs to be followed in order), the internal routing can be modified towards the necessary virtual network card or reset towards the regular real network card.

This project started in 2014 as a prototype for university research purposes at the UTT (*Université de Technologie de Troyes*). As of today, it is at an (early) alpha stage. Originally thought, designed and coded by Ferdinand Bellissime (*Guzmud*) and Jean-Baptiste Truffault (*zaralger*), under the initial supervision of M. Cogranne.

User guide
----------

Regarding installation, there is no assistant yet. Dependencies are *Python* (2.7 recommended), a virtual interface (*tuntap* for windows, *dummy interface* for linux), *pcap* and its associated wrapper (like *WinPcap* and Maissom Ciani's *winpcapy* under Windows). A small untranslated documentation can be found inside the project, which should give birth to an assistant in the future.

Legba should assist you to select the virtual and the real interfaces, configure the network engine and the virtual interface, and modify the route (to use the real or virtual interface as the default route).

Anansi allows you to manage the spiders (the underlying processes running the different pieces of the modules), the buffers between them, to manage the scenarios (the sets of configuration for the modules, archived in the scenarios folder) and to manage the applications (which are running over the hidden channel). Only two applications are developed for the moment, sending random ASCII chars (for lab testing) and transferring a file (please notice the reception isn't stable yet, and there is no additional mechanism for the transfer).

Dev guide
---------

Anansi is articulated around three levels : network, information, application.

The network level manipulates interfaces to intercept network data, exchange it with the craft level, and inject it in the other interface (in our case, between a virtual interface becoming the main exit point for the OS and the usual real interface). It takes care of mac addresses translation, IP addresses translation, level-3 and level-4 checksums. It can be forked to provide support for other kinds of network applications.

The craft level is the steganographic engine. It exchanges data with both the network and the application levels. Besides the insertion and extraction of steganographic data, it can provide a light flag system. For the moment, the craft level is quite locked around network steganography through binary substitution but should evolve to provide new functionalities.
	
The application level is made of all the homebrew applications available. At this stage of the project, a lab testing application (sending k random chars) and a crude file exchange application exist. Once the two other levels are more stable, the potential of the solution and the available applications should expend. The applications are completed by information treatments, like a Lagrangian interpolation system (providing repetition without redundancy). A LFSR module (modifying the steganographied data to limit spectral analysis) is being rewritten, and with time, new information treatments should appear.

Apart from the solution components, you may also find different useful libraries (checksums, shamir, etc.).

Note that the whole solution was developed following a few key concepts : *aiming for a modular and adaptive project* (to easier development, forks and reuse), *maximizing the independence from an specific OS or platform* (though you need some parts to be OS-specific), *minimizing the exterior dependencies* (between the DIY directive and a strategical choice to survive).

Non-authoritative todo list
---------------------------

*Short-term*, for everything is not perfect
- rework the scenarii system
- rework the configuration and global variables system
- stabilise file exchange
- implement application level module system
- implement application level protocol system
- save default conf for an automated legba / load net conf
- add the documentation
	
*Middle-term*, for there is still road ahead
- implement application level protocol
- application : chat
- modules : lsfr/msequence, matrix embedding
- protocols : XMPP and IRC, SMTP/IMAP/POP3, TORRENT, FTP, HTTP, Telnet and SSH
- pre-made scenarios : VoIP channel, web exchange
- translate the documentation
	
*Long-term*, for we should never forget it
- IPv6 compatibility
- Linux portability (dynamic pcap import according to configuration/os-detection)
- GUI
- framework orientation and dynamical worker import
- high-level and embedded data steganography (DPI-style)
- application : network output of a virtual machine
- new craft : late voip

Thanks to
---------

- M. Cogranne and the UTT
- Maissom Ciani, for winpcapy (2009)