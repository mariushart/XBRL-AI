#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 09:40:44 2018

@author: niels-peter
"""

__title__ = 'XBRL-AI'
__version__ = '0.0.2'
__author__ = 'Niels-Peter Rønmos'

import requests
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring

def XBRLinstance_to_dict(XBRLinstance): 
    """
    Transforming XBRL-instant to python dictionary 
    """
    ## From XBRL to dict
    XBRLdict = bf.data(fromstring(XBRLinstance))['{http://www.xbrl.org/2003/instance}xbrl']    

    ## Extract unit information
    UN = {}   
    unit = XBRLdict['{http://www.xbrl.org/2003/instance}unit']
    if type(unit).__name__ == 'list':
        for post in unit:
            UN[post['@id']] = (post['{http://www.xbrl.org/2003/instance}measure'])['$']   
    if type(unit).__name__ == 'OrderedDict':
        UN[unit['@id']] = (unit['{http://www.xbrl.org/2003/instance}measure'])['$']    
    contexts = XBRLdict['{http://www.xbrl.org/2003/instance}context']
    
    ## Extract context information
    CO = {}
    for post in contexts:
        identifier = scheme = startDate = endDate = instant = explicit = typed = None
        entity = post['{http://www.xbrl.org/2003/instance}entity']
        for element in entity:
            identifier = (entity[element])['$']
            scheme = (entity[element])['@scheme']
        period = post['{http://www.xbrl.org/2003/instance}period']
        try: startDate = (period['{http://www.xbrl.org/2003/instance}startDate'])['$']
        except: startDate = None
        try: endDate = (period['{http://www.xbrl.org/2003/instance}endDate'])['$']
        except: endDate = None
        try: instant = (period['{http://www.xbrl.org/2003/instance}instant'])['$']
        except: instant = None
        try: explicit = (post['{http://www.xbrl.org/2003/instance}scenario'])['{http://xbrl.org/2006/xbrldi}explicitMember']
        except: pass
        try: typed = (post['{http://www.xbrl.org/2003/instance}scenario'])['{http://xbrl.org/2006/xbrldi}typedMember']        
        except: pass         
        CO[post['@id']] = [identifier, scheme, startDate, endDate, instant, explicit, typed]
    
    ## Remove unit and context information as they are extracted
    for opryd in ('{http://www.xbrl.org/2003/instance}context', '{http://www.xbrl.org/2003/instance}unit'):
        del XBRLdict[opryd]
        
    ## Add unit and context infdromation on concepts    
    for concept in XBRLdict:
        if type(XBRLdict[concept]).__name__ == 'OrderedDict':
            try: (XBRLdict[concept])['context'] = CO[(XBRLdict[concept])['@contextRef']]
            except: pass
            try: (XBRLdict[concept])['unit'] = UN[(XBRLdict[concept])['@unitRef']]
            except: pass
        if type(XBRLdict[concept]).__name__ == 'list':
            for i in range(0, len(XBRLdict[concept])):
                try: ((XBRLdict[concept])[i])['context'] = CO[((XBRLdict[concept])[i])['@contextRef']]
                except: pass
                try: ((XBRLdict[concept])[i])['unit'] = UN[((XBRLdict[concept])[i])['@unitRef']]
                except: pass
    return XBRLdict


##test
#target_url = "http://regnskaber.virk.dk/27851382/ZG9rdW1lbnRsYWdlcjovLzAzLzY4L2U1LzgyLzNlLzFmOGMtNDJiNS05MDNjLWUwYWI5OTMzNTg1MA.xml"
#file_indhold = requests.get(target_url).content 
#sample = XBRLinstance_to_dict(file_indhold)