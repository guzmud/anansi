#! /usr/bin/python

import os, inspect
import xml.etree.ElementTree as ET

## FX

def unPaquet(bitList, protocolName):
     fullpath = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))),'protocols',str(protocolName)+'.xml') #tree = ET.parse("protocols/" +protocolName +".xml")
     tree = ET.parse(fullpath)
     root = tree.getroot()

     globalCursor=0 # init position=0
     newHeader = []
     
     for field in root:
          field_name = field.find("name").text
          field_size = int(field.find("size").text)
          
          if field.attrib and int(field.attrib["dynamical"]) == 1:
               dynamicalField = field.find("dynamical")
               if dynamicalField.find("multiplicatorField") is not None:
                    multiplicatorField = dynamicalField.find("multiplicatorField").text
                    #multiplicatorFieldValue = newHeader.fields[multiplicatorField]["value"] # /!\
                    multiplicatorFieldValue = filter(None,[k["value"] if k["name"]==multiplicatorField else '' for k in newHeader])[0]
                    multiplicator = int(str(multiplicatorFieldValue),2)
                    
               else:
                    conditionnalField = dynamicalField.find("conditionnalField").text
                    #conditionnalFieldValue = newHeader.fields[conditionnalField]["value"]# /!\
                    conditionnalFieldValue = filter(None,[k["value"] if k["name"]==conditionnalField else '' for k in newHeader])[0]
                    moreThan = int(dynamicalField.find("moreThan").text)
            
                    if int(str(conditionnalFieldValue),2) > moreThan:
                         multiplicator = int(dynamicalField.find("multiplicator").text)
                    else: 
                         multiplicator = int(dynamicalField.find("ifNOTmultiplicator").text)
            
               field_size = multiplicator * field_size
                
          field_workable = bool(field.find("workable").text.lower() in ["true"])
          value = bitList[globalCursor:globalCursor+field_size]

          newHeader += [{"name":field_name,"position":globalCursor,"size":field_size,"workable":field_workable,"value":value}]
          
          globalCursor += field_size
          # protocols[protocolName]=[root.attrib["level"],newHeader] # WTF ? useless ?
     
     data = bitList[globalCursor:] # position

     return newHeader, data

def repaquet(headerList, data):
     newPaquet = ""
     for header in headerList:
          for field in header: # verifier/enforcer l'ordre numerique des fields ?
               newPaquet += str(field["value"])
     newPaquet += ''.join(list(data))
     return newPaquet
