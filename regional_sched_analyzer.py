# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 14:08:51 2015

@author: stat
"""

from bs4 import BeautifulSoup
from urllib import request
from pprint import pprint



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
    datedict = {}
    
    datetablerows = soup.find_all('tr', bgcolor='#FFFFFF')
   
    week0 = '24-Feb - 27-Feb-2016'    
    
    for row in datetablerows:
        eventdict = {}
        
        items = row.find_all('td')
        
        print('\nEvent Name', items[1].a.contents)

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
            
        pprint(eventdict)
    
    print()
    
    return datedict






        
def test():
    
    with open('currentsched.html') as file:
        
        htmldata = file.read()
        #print(htmldata)
        
        datedict = get_dates(htmldata)
    
   
test()

