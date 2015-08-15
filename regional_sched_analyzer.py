# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 14:08:51 2015

@author: stat
"""

from bs4 import BeautifulSoup
from urllib import request



def get_schedule(year):
    
    baseurl = 'https://my.usfirst.org/myarea/index.lasso?event_type=FRC&year='
    
    fullurl = baseurl + year
    
    firstpage = request.urlopen(fullurl)

    assert firstpage.status == 200

    return firstpage.read()
    
def get_dates(datepage):
    
    soup = BeautifulSoup(datepage.read(), 'html.parser')
    
    print(soup.prettify)
    
    
def makefile():
    
    year = '2016'
    
    with open('currentsched.html','w') as outfile:
        soup = BeautifulSoup(get_schedule(year), 'html.parser')
        outfile.write(str(soup.prettify))
        
def test():
    
    with open('currentsched.html') as file:
        
        htmldata = file.read()
        
        print(htmldata)
    

    


