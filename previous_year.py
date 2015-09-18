# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 19:17:20 2015

@author: stat
"""

from bs4 import BeautifulSoup
from urllib import request
from pprint import pprint
import datetime
import requests
import pandas

year = '2015'


def get_schedule(year):
    
    baseurl = 'https://my.usfirst.org/myarea/index.lasso?event_type=FRC&year='
    
    fullurl = baseurl + year
    print('Accessing URL', fullurl)
    firstpage = request.urlopen(fullurl)   
    #Let's error out right now if the FIRST site is not cooperating
    assert firstpage.status == 200  

    return firstpage.read()
    
    
def makefile():
    
    with open('lastyear.html','w') as outfile:
        soup = BeautifulSoup(get_schedule(year), 'html.parser')
        outfile.write(str(soup.prettify))
        
        print('File written')
        
def html2df_schedule(filename):
    eventitems = ['type', 'name', 'venue', 'location', 'dates']    
    
    with open(filename, 'r') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
        datelist = []
    
        datetablerows = soup.find_all('tr', bgcolor='#FFFFFF')
    
 
        for row in datetablerows:
            eventdict = {}
            
            items = row.find_all('td')
            
            #print('Event Name', items[1].a.contents)
            
            for idx in range(len(eventitems)):
                
                if idx != 1:
                    if len(items[idx].contents) == 1:
                        eventdict[eventitems[idx]] = items[idx].contents[0].strip('\n\t').replace(u'\xa0',',')
                    else:
                        i = str(items[idx].contents[1]).lstrip('<em>').rstrip('</em>') 
                        i = i + ' ' + items[idx].contents[3].strip('\n\t')
                        eventdict[eventitems[idx]] = i

                else: #name is formatted differently
                    eventdict[eventitems[idx]] = items[idx].a.contents[0]
                    
                    #eventdict['week'] = getweeknum(eventdict['dates'], week0saturday)
                    #print(eventdict)
        
                #if eventdict['type'] == 'Regional':
                    #eventdict['name'] = trimnames(eventdict['name'])
            datelist.append(eventdict.copy())
            #print(len(datelist))
                    
    schedule = pandas.DataFrame(datelist, index = range(len(datelist)))
    #pprint(schedule)
    return schedule
        
        
if __name__ == "__main__":
    #makefile()

    lastYear = html2df_schedule('lastyear.html')
    pprint(lastYear[lastYear['type'] == 'Regional']['name'])
    
    thisYear = html2df_schedule('currentsched.html')
    pprint(thisYear[thisYear['type'] == 'Regional']['name'])