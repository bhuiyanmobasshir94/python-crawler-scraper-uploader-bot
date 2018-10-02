#!/bin/python
# -*- coding: utf-8 -*-
from time import sleep
import requests
from bs4 import BeautifulSoup
import re
import scraper as scrape
import listings_uploader_bot as lsb
import os, csv
from datetime import datetime

user = '' # username
password = '' # password

start_time = datetime.now().time()
print("Starting time: {}h :{}m :{}s".format(start_time.hour,start_time.minute,start_time.second))
def getFirstLink():
    response = requests.get('https://boat.me/boats/find/1/reservationType1/',auth=(user, password),verify=True)
    if response.status_code != requests.codes.ok:
        getFirstLink()
    return response

soup = BeautifulSoup(getFirstLink().content,"lxml")
totalpages = (soup.find(class_="pages-range").select("strong:nth-of-type(1)")[0].text.strip())[4:6]
totalboats = soup.find(class_="pages-range").select("strong:nth-of-type(2)")[0].text.strip()

boatlinks = []
errorpages = []
def getLinks():
    boatlinks.clear()
    for a in range(1,int(totalpages)+1):
        page = requests.get('https://boat.me/boats/find/'+str(a)+'/reservationType1/',auth=(user, password),verify=True)
        if page.status_code == requests.codes.ok:
           soup1 = BeautifulSoup(page.content,"lxml")
           links = soup1.find_all(class_="boat-info")
           for link in links:
               boatlinks.append(link.select('a')[0]['href'])
        else:
           print("Getting error for page number " + str(a) )
           errorpages.append(str(a))
    return

def checkLinks():
    if(len(boatlinks) == int(totalboats)):
        print("Successfully got all the boats " + str(len(boatlinks)))
        return
    else:
        getLinks()
        checkLinks()
    return
try:
    getLinks()
    checkLinks()
except Exception:
    checkLinks()

listings_uploader_bot = lsb.ListingUploader()
listings_uploader_bot.strart_up()

i = 1
for boat in boatlinks:
    listing_start = datetime.now().time()
    print(i)
    i += 1
    try:
        raw = requests.get('https://boat.me'+ boat,auth=(user, password),verify=True) 
        if raw.status_code == requests.codes.ok:
            soup = BeautifulSoup(raw.content,"lxml")
            output = scrape.scrape_listing(soup)
            #listings_uploader_bot.post_new_listings(output)
            print("Title: {} & State: {}".format(output['scraped_title'],output['scraped_state']))
        listing_end = datetime.now().time()
        print("Listing scrape & Upload time: {}h :{}m :{}s".format((listing_end.hour-listing_start.hour),(listing_end.minute-listing_start.minute),(listing_end.second-listing_start.second)))
    except Exception:
        print("Exception from: scraper & uploader")
        pass

listings_uploader_bot.ending()

ending_time = datetime.now().time()
print("Total time taken: {}h :{}m :{}s".format(ending_time.hour,ending_time.minute,ending_time.second))
        
