# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 14:08:51 2015

@author: stat
"""

from bs4 import BeautifulSoup
from urllib import request
from pprint import pprint
import datetime



def get_schedule(year):
    
    baseurl = 'https://my.usfirst.org/myarea/index.lasso?event_type=FRC&year='
    
    fullurl = baseurl + year
    
    firstpage = request.urlopen(fullurl)   
    #Let's error out right now if the FIRST site is not cooperating
    assert firstpage.status == 200  

    return firstpage.read()
    
    
def makefile():
    
    year = '2016'
    
    with open('currentsched.html','w') as outfile:
        soup = BeautifulSoup(get_schedule(year), 'html.parser')
        outfile.write(str(soup.prettify))
        
    
def get_dates(datepage):
    
    soup = BeautifulSoup(datepage, 'html.parser')
    eventitems = ['type', 'name', 'venue', 'location', 'dates']    
    datelist = []
    
    datetablerows = soup.find_all('tr', bgcolor='#FFFFFF')
    
    week0saturday = datetime.date(2016,2,27)
  
    for row in datetablerows:
        eventdict = {}
        
        items = row.find_all('td')
        
        print('Event Name', items[1].a.contents)

        for idx in range(len(eventitems)):
            
            if idx != 1:
                if len(items[idx].contents) == 1:
                    eventdict[eventitems[idx]] = items[idx].contents[0].strip('\n\t')
                else:
                    i = str(items[idx].contents[1]).lstrip('<em>').rstrip('</em>') 
                    i = i + ' ' + items[idx].contents[3].strip('\n\t')
                    eventdict[eventitems[idx]] = i

            else: #name is formatted differently
                eventdict[eventitems[idx]] = items[idx].a.contents[0]
            
        eventdict['week'] = getweeknum(eventdict['dates'], week0saturday)
        datelist.append(eventdict.copy())
    
    pprint(datelist)
    
    return datelist

def getweeknum(eventdates, firstsat):
    '''
    eventdates is a string formatted:
    02-Mar - 05-Mar-2016  
    dd-mmm - dd-mmm-yyyy
    01234567890123456789
    '''
    firstweek = 0  #special for 2016    
    
    
    endday = datetime.datetime.strptime(eventdates[9:], '%d-%b-%Y')
    
    endday = datetime.date(endday.year, endday.month, endday.day)
        
    for i in (range(8)):
        dayssince1 = 7 * i
        
        currentsat = firstsat + datetime.timedelta(dayssince1)
        #print(currentsat)
        
        #Event end runs Tuesday to Monday
        weekstart = currentsat - datetime.timedelta(4)
        weekend = currentsat + datetime.timedelta(2)
        
        #print(type(weekstart), type(endday), type(weekend))
        
        if weekstart < endday < weekend:
            #print('got it')
            return i
        
        

    print('Error: No week found', endday)
    return None
    

        
def test():
    
    with open('currentsched.html') as file:
        
        htmldata = file.read()
        #print(htmldata)
        
        eventlist = get_dates(htmldata)
    
   
test()

