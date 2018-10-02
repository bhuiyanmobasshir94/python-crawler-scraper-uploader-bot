#!/bin/python
# -*- coding: utf-8 -*-

import math
import requests
from bs4 import BeautifulSoup
import re
import os,csv
import pgeocode

def scrape_title(soup):
  raw_title = soup.find("div",class_="boat-info").select("h1:nth-of-type(1)")[0].text
  title = ' '.join(raw_title.split())
  return title

def scrape_gallery_images(soup):
  image_links = [] #All the image links on that particular boat page
  raw_image = soup.find(class_="bxslider")
  raw_image_1 = [img.attrs['style'].split('(')[1] for img in raw_image.findAll("li")]
  raw_image_2 = [img1.split(')')[0] for img1 in raw_image_1]
  images = [img3.strip('"') for img3 in raw_image_2]
  for each in images:
    image_links.append("https://boat.me"+each)
  return image_links

def scrape_captain_image(soup):
  raw_image_captain = soup.find("div",class_="owner-thumb").attrs['style'].split("(")[1]
  captain_image = "https://boat.me"+raw_image_captain.split(")")[0]
  return captain_image

def scrape_captain_name(soup):
  captain_name = soup.find("span",class_="owner-name").text.strip()
  return captain_name

def scrape_everyday_price(soup):
  raw_price = soup.find("div",class_="daily-price-info-boat").select("span:nth-of-type(1)")[0].text
  raw1= ''.join(raw_price.split())
  raw2 = ''.join(raw1.split("$"))
  try:
    price_per_day = int(raw2.split("p")[0])
    return price_per_day
  except Exception:
    price_per_day = int((raw2.split("p")[0]).split("/")[0])
    return price_per_day

def scrape_every_sevenday_price(soup):
  raw_price = soup.find("div",class_="daily-price-info-boat").select("span:nth-of-type(3)")
  if raw_price:
    raw2= raw_price[0].text
    raw3= ''.join(raw2.split())
    raw4 = ''.join(raw3.split("$"))
    price_over_seven_day = int(raw4.split("/")[0])
    return price_over_seven_day
  else:
    return int(0)

def scrape_captained_bareboat_info(soup):
  raw_captained = soup.find("div",class_="item-type").select("span:nth-of-type(1)")[0].text
  captained_bareboat_info = ' '.join(raw_captained.split())
  return captained_bareboat_info

def scrape_location(soup):
  raw_location = soup.find("span",class_="location").select("a")[0].text
  location = ' '.join(raw_location.split())
  return location

def scrape_built_year(soup):
  raw_year = soup.find("span",class_= re.compile("^boat-type")).text
  built_year = ' '.join(raw_year.split())
  return built_year

def scrape_people(soup):
  raw_people = soup.find("span",class_="people").text
  people = ' '.join(raw_people.split()) 
  return people

def scrape_map(soup):
  raw_map = soup.find("div",class_="content").select("script:nth-of-type(2)")[0].text
  raw_map2 = re.search(r'LatLng\((.+?)\)', raw_map).group(1)
  raw_map3 = ''.join(raw_map2.split())
  raw_map4 = ''.join(raw_map3.split('"'))
  lat,lng = raw_map4.split(",")
  return lat,lng

def scrape_relevent_contents(soup):
  boatinfos={}
  additionalcharges = {}
  specifications = {}
  additionalamenities = [] 
  targets = soup.find_all("div",class_="title")
  for target in targets:
    if target.text == "Boat info":
      infos = target.next_sibling.find_all("div", class_="col")
      for info in infos:
        info1 = ' '.join(info.text.split())
        info2 = info1.split(":")
        boatinfos[info2[0]] = info2[1]
    elif target.text == "Additional Charges (Daily)":
      charges = target.next_sibling.find_all("div", class_="col")
      for charge in charges:
        charge1 = ' '.join(charge.text.split())
        charge2 = charge1.split(":")
        additionalcharges[charge2[0]] = charge2[1]
    elif target.text == "Boat specification":
      specs = target.next_sibling.find_all("div", class_="col")
      for spec in specs:
        spec1 = ' '.join(spec.text.split())
        spec2 = spec1.split(":")
        if type(spec2) is list:
          for c in spec2:
            if c != spec2[0]:
              specifications[spec2[0]] = c
        spec3 = spec1.split(' ')
        if(spec3[0]== "Type"):
            specifications[spec3[0]] = spec3[1] 
    elif target.text == "Additional amenities":
      amenities = target.next_sibling.find_all("div", class_="col")
      for amenity in amenities:
        amenity1 = ' '.join(amenity.text.split())
        additionalamenities.append(amenity1)
    else:
      continue
  return boatinfos,specifications,additionalcharges,additionalamenities

def scrape_boat_description(soup):
  targets = soup.find_all("div",class_="title")
  for target in targets:
    if target.text == "Boat description":
      description = target.next_sibling.text.strip()
  return description

def scrape_boat_infos(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  desc_boatinfo = '[stm_tech_infos title="BOAT INFO"]'
  for value in boatinfos.keys():
    desc_boatinfo += '[stm_tech_info name="'+value+'" value="'+boatinfos[value]+'"]'
  desc_boatinfo += '[/stm_tech_infos]'
  return desc_boatinfo

def scrape_boat_specifications(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  desc_boatspec = '[stm_tech_infos title="BOAT SPECIFICATION"]'
  for value in specifications.keys():
    desc_boatspec += '[stm_tech_info name="'+value+'" value="'+specifications[value]+'"]'
  desc_boatspec += '[/stm_tech_infos]'
  return desc_boatspec

def scrape_boat_additional_charges_daily(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  desc_additional_charges = '[stm_tech_infos title="ADDITIONAL CHARGES (DAILY)"]'
  for value in additionalcharges.keys():
    desc_additional_charges += '[stm_tech_info name="'+value+'" value="'+additionalcharges[value]+'"]'
  desc_additional_charges += '[/stm_tech_infos]'
  return desc_additional_charges

def scrape_boat_additional_amenities(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  desc_additional_amenities = '[stm_tech_infos title="ADDITIONAL AMENITIES"][/stm_tech_infos]<ul class="list-style-2"><table>'
  total_number = len(additionalamenities)
  turns_to_take = math.ceil(total_number/4)
  for x in range(0,turns_to_take+1):
    desc_additional_amenities += '<tr>'
    for y in range(0,4):
      z = x*3
      w = x+y+z
      if(w<total_number):
        desc_additional_amenities += '<td><li>'+additionalamenities[w]+'</li></td>'
      else:
        continue
    desc_additional_amenities += '</tr>'
  desc_additional_amenities += '</table></ul>'
  return desc_additional_amenities

def scrape_length(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  for value in specifications.keys():
    if value == "Total Length": 
      length = ' '.join(specifications[value].split()) 
      return length

def scrape_model(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  for value in specifications.keys():
    if value == "Model":
      model = ' '.join(specifications[value].split()) 
      return model

def scrape_boat_type(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  for value in specifications.keys():
    if value == "Type":
      boat_type = ' '.join(specifications[value].split()) 
      return boat_type

def scrape_damage_deposite(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  for value in additionalcharges.keys():
    if value == "Damage Deposit":
      damage_deposite = ' '.join(additionalcharges[value].split()) 
      return damage_deposite
  return ''

def scrape_fuel_expenses(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  for value in additionalcharges.keys():
    if value == "Approx. Fuel Exp.":
      fuel_expenses = ' '.join(additionalcharges[value].split())
      return fuel_expenses
  return ''
  

def scrape_captain_service(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  for value in additionalcharges.keys():
    if value == "Captain Service":
      raw_captain_service =''.join(additionalcharges[value].split())
      raw_captain_service1 = ''.join(raw_captain_service.split("$"))
      captain_service = int(raw_captain_service1.split("/")[0])
      return captain_service
  return int(0)

def scrape_state(soup):
  boatinfos,specifications,additionalcharges,additionalamenities = scrape_relevent_contents(soup)
  for value in boatinfos.keys():
    if value == "Address":
      if boatinfos[value].split(",")[-1]:
        state = ''.join(boatinfos[value].split(",")[-1])
        return state 
      else:
         for value in boatinfos.keys():
             if value == "Zip Code":
               nomi = pgeocode.Nominatim('us')
               state = nomi.query_postal_code(boatinfos[value]).state_code
               return state
  return "N/A"

###################################### API Calling Zone ##########################################
def scrape_listing(raw_html):
  scraped_listing_archive = {}    
  scraped_listing_archive['scraped_title'] = scrape_title(raw_html)#
  scraped_listing_archive['scraped_gallery'] = scrape_gallery_images(raw_html)#
  scraped_listing_archive['scraped_captain_image'] = scrape_captain_image(raw_html)#//__\\
  scraped_listing_archive['scraped_captain_name'] = scrape_captain_name(raw_html)#//__\\
  scraped_listing_archive['scraped_everyday_price'] = scrape_everyday_price(raw_html)#
  scraped_listing_archive['scraped_over_sevenday_price'] = scrape_every_sevenday_price(raw_html)#
  scraped_listing_archive['scraped_captained_bareboat'] = scrape_captained_bareboat_info(raw_html)#
  scraped_listing_archive['scraped_location'] = scrape_location(raw_html)#
  scraped_listing_archive['scraped_built_year'] = scrape_built_year(raw_html)#
  scraped_listing_archive['scraped_people'] = scrape_people(raw_html)#
  raw_scraped_latitude,raw_scraped_longitude = scrape_map(raw_html)
  scraped_listing_archive['scraped_latitude'] = raw_scraped_latitude#
  scraped_listing_archive['scraped_longitude'] = raw_scraped_longitude#
  #scrape_relevent_contents(raw_html) # *** (-_-)
  scraped_listing_archive['scraped_description'] = scrape_boat_description(raw_html)#
  scraped_listing_archive['scraped_boat_info'] = scrape_boat_infos(raw_html)#
  scraped_listing_archive['scraped_boat_specification'] = scrape_boat_specifications(raw_html)#
  scraped_listing_archive['scraped_daily_additional_charges'] = scrape_boat_additional_charges_daily(raw_html)#
  scraped_listing_archive['scraped_additional_amenities'] = scrape_boat_additional_amenities(raw_html)#
  scraped_listing_archive['scraped_length'] = scrape_length(raw_html)#
  scraped_listing_archive['scraped_model'] = scrape_model(raw_html)#
  scraped_listing_archive['scraped_boat_type'] = scrape_boat_type(raw_html)#
  scraped_listing_archive['scraped_damage_deposite'] = scrape_damage_deposite(raw_html)#
  scraped_listing_archive['scraped_fuel_expenses'] = scrape_fuel_expenses(raw_html)#
  scraped_listing_archive['scraped_captain_service'] = scrape_captain_service(raw_html)#
  scraped_listing_archive['scraped_state'] = scrape_state(raw_html)#
  return scraped_listing_archive

