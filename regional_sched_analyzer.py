# -*- coding: utf-8 -*-
"""
Created on Sat Aug 15 14:08:51 2015

@author: stat
"""

from bs4 import BeautifulSoup
from urllib import request
from pprint import pprint
import datetime
import requests

year = 2016

blockedweeks = [3,4] #weeks of Barstow Spring Break

def get_schedule(year):
    
    baseurl = 'https://my.usfirst.org/myarea/index.lasso?event_type=FRC&year='
    
    fullurl = baseurl + year
    
    firstpage = request.urlopen(fullurl)   
    #Let's error out right now if the FIRST site is not cooperating
    assert firstpage.status == 200  

    return firstpage.read()
    
    
def makefile():
    
    #year = '2016'
    
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
            
        eventdict['week'] = getweeknum(eventdict['dates'], week0saturday)
        datelist.append(eventdict.copy())
    
    #pprint(datelist)
    
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

def prepmaprequest(orig,destlist):
    '''(str, list of str)
    
    '''

    matrixrqst = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    
    origins = 'origins=' + space2plus(orig)
    
    destinations = 'destinations=' + space2plus(pipdelim(destlist))
    
    keyfile = open('C:\\Users\\stat\\Documents\\SecretSquirrel\\googleapikey.txt','r')
    key = 'key=' + keyfile.read()   
    keyfile.close()
    
    units = 'units=imperial'
    
    maprequest = matrixrqst + '&'.join([origins, destinations, units, key])
    
    return maprequest

def space2plus(urlstring):
    '''(str)-> str
    Replaces all spaces in the input string with + characters for inclusion in a url.
    '''
    #find the unicode line break
    
    linebreak = urlstring.find(u'\xa0')
    
    result = urlstring.replace(' ', '+').replace(',','')
       
    return result

def pipdelim(loclist):
    '''(list of str)-> str
    Convert location list to a pipe delimited string
    '''

    result = '|'.join(loclist)   
    
    return result


def formLocationList(eventlist):
    '''(list of dictionary) -> list of str
    
    Return the regional locations as a list.
    '''

    loclist = []
        
    print('Non-regional or duplicate:')
    for event in eventlist:
        if event['type'] == 'Regional' and event['location'] not in loclist:
            loclist.append(event['location'])
        else:
            print(" ",event['location'],event['type'])

    return loclist


def getdistancematrix(url):
    '''(str) -> json object
    '''
    
    response = requests.get(url)
    
    print('Sending mileage matrix query to google\n')
    
    if response.status_code == 200:
        return response.json()

def mergeEventMilage(eventlist, milagemtx):
    '''(list of dict, JSON object) -> list of dict
    
    This function will find the mileage and drive time for each event, 
    returning a record like this:
     [{'dates': '31-Mar - 02-Apr-2016',
       'distance': '993 mi',
       'distmeters': 1598704
       'duration': '14 hours 47 mins',
       'location': 'Oregon City, OR USA',
       'name': 'PNW District - Oregon City Event',
       'status': 'OK',
       'type': 'Pacific Northwest District Event',
       'venue': 'Clackamas Academy of Industrial Sciences',
       'week': 5},{...}]
       
     Records containing non-regional events will not gain distance, duration, and status
     information
     Records containing status other than ok will default to 12000 miles and 171 hours
     Which is roughly half the circumferance of the earth and the drive time
     to get there at 70 mph (not accounting for minor inconveniences like oceans)
    '''
    for eventidx in range(len(eventlist)):
        loc = eventlist[eventidx]['location']
        
        problemlocs = {'St. Louis, MO, USA': 'Saint Louis, MO, USA',
                       'Tel Aviv, TA, Israel': "HaTa'asiya Street, Tel Aviv-Yafo, Israel"}
        
        if loc in problemlocs:
            loc = problemlocs[loc]
        
        if loc in milagemtx['destination_addresses']:
            idx = milagemtx['destination_addresses'].index(loc)
            #print(loc, idx)
            status = milagemtx['rows'][0]['elements'][idx]['status']
            if status == 'OK':
                distance = milagemtx['rows'][0]['elements'][idx]['distance']['text']
                dm = milagemtx['rows'][0]['elements'][idx]['distance']['value']
                drivetime = milagemtx['rows'][0]['elements'][idx]['duration']['text']
                #print(loc, distance, drivetime)
            else:
                #print(loc, milagemtx['rows'][0]['elements'][idx]['status'])
                distance = '1200 mi'
                drivetime = '7 days 3 hours'
                dm = 1931210
            
            eventlist[eventidx]['distance'] = distance
            eventlist[eventidx]['distmeters'] = dm            
            eventlist[eventidx]['duration'] = drivetime
            eventlist[eventidx]['status'] = status
                
        elif eventlist[eventidx]['type'] == 'Regional':
            print(" ",loc, 'not found in milagemtx')

    return eventlist
    ###COOK
    ### Next step is to do pandas to get the easy ability to generate a results list


def parsefrcschedule():
    
    with open('currentsched.html') as file:
        
        htmldata = file.read()
        #print(htmldata)
        
        eventlist = get_dates(htmldata)
        print('Data found for', len(eventlist), 'events\n')
        #pprint(eventlist)
        
        regionalLocs = formLocationList(eventlist)        
        print('\nPreparing mileage search for', len(regionalLocs), 'Regional events\n')
        maprequest = prepmaprequest('Kansas City, MO', regionalLocs)
        
        dmatrix = getdistancematrix(maprequest)           
        #pprint(dmatrix)
        
        print('Merging distance and event information\n')
        mergeEventMilage(eventlist, dmatrix)
        
        pprint(eventlist)
   
parsefrcschedule()

