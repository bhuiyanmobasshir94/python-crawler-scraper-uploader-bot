#!/bin/python
# -*- coding: utf-8 -*-

from time import sleep
from random import randint
import selenium
#from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver import DesiredCapabilities
#from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests


class ListingUploader():
	def __init__(self):
		self.wp_admin = "https://charter.needboat.com/wp-admin"
		self.add_new_listings = "https://charter.needboat.com/wp-admin/post-new.php?post_type=listings"

	# Open headless chromedriver
	def start_driver(self):
		try:
			print('starting driver...')
			self.driver = webdriver.Chrome(r"C:\chromedriver.exe")
			self.driver.maximize_window()
			sleep(1)
		except Exception as e:
			print('Exception from: start_driver',e)
			pass

	def close_driver(self):
		try:
			print('closing driver...')
			#self.display.stop()
			self.driver.quit()
			print('closed!')
		except Exception as e:
			print('Exception from: close_driver',e)
			pass
        
	def get_page(self, url):
		try:
			print('browsing upload page...')
			self.driver.get(url)
			sleep(1)
		except Exception as e:
			print('Exception from: get_page',e)
			pass

	def login(self):
		print('logging in to the wp-admin...')
		try:
			form = self.driver.find_element_by_xpath('//*[@id="loginform"]')
			form.find_element_by_xpath('.//*[@id="user_login"]').send_keys() # username credentials
			form.find_element_by_xpath('.//*[@id="user_pass"]').send_keys() # password credentials
			form.find_element_by_xpath('.//*[@id="wp-submit"]').click()
			sleep(2)
		except Exception as e:
			print('Exception from: login',e)
			pass
	
	def title(self,output):
		try:
			self.driver.execute_script("document.querySelector('div#titlewrap>input').value ='{}'".format(output['scraped_title']))
			sleep(1)
		except Exception as e:
			print('Exception from: title',e)
			pass

	def backend_editor_mapping(self,output):
		try:
			self.driver.execute_script("document.querySelectorAll('div.vc_tta-tabs-container>ul.vc_tta-tabs-list>li>a')[4].click()")
			self.driver.execute_script("document.querySelectorAll('div.wpb_stm_gmap>div.vc_controls>div.vc_controls-cc>a')[1].click()")
			sleep(3)
			self.driver.execute_script("document.querySelector('div.edit_form_line>input.lat').value = '{}'".format(output['scraped_latitude']))
			self.driver.execute_script("document.querySelector('div.edit_form_line>input.lng').value = '{}'".format(output['scraped_longitude']))
			sleep(1)
			self.driver.execute_script("document.querySelectorAll( 'div.vc_ui-button-group>span' )[1].click()")
			self.driver.execute_script("window.scrollBy(0,300)")
		except Exception as e:
			print('Exception from: backend_editor_mapping',e)
			pass

	def listing_manager(self,output):
		try:
			'''
			listing_manager = self.driver.execute_script("document.querySelector('div#butterbean-ui-stm_car_manager').getAttribute('class')").split()
			if len(listing_manager) == 2:
				self.driver.execute_script("document.querySelector('div#butterbean-ui-stm_car_manager>button').click()")
				sleep(1)
			'''
			self.driver.execute_script("document.querySelectorAll( 'div#butterbean-manager-stm_car_manager>ul>li>a' )[0].click()")
			sleep(1)
			#self.driver.execute_script("document.querySelector( 'div.stm_car_location_admin>input#stm_car_location' ).value = '{}'".format(output['scraped_location']))
			self.driver.find_element_by_xpath("//input[@id='stm_car_location']").send_keys(output['scraped_location'])
			sleep(1)
			self.driver.find_element_by_xpath("//input[@id='stm_car_location']").send_keys(Keys.ARROW_DOWN)
			self.driver.find_element_by_xpath("//input[@id='stm_car_location']").send_keys(Keys.ENTER)
			self.driver.execute_script("document.querySelectorAll( 'div#butterbean-manager-stm_car_manager>ul>li>a' )[1].click()")
			sleep(1)
			self.driver.execute_script("document.querySelector('div#butterbean-control-serie>div.stm-multiselect-wrapper>div.stm_add_new_optionale>div.stm_add_new_inner>input').value = '{}'".format(output['scraped_model']))
			self.driver.execute_script("document.querySelector('div#butterbean-control-serie>div.stm-multiselect-wrapper>div.stm_add_new_optionale>div.stm_add_new_inner>i').click()")
			sleep(1)	
			self.driver.execute_script("document.querySelector('div#butterbean-control-boat-type>div.stm-multiselect-wrapper>div.stm_add_new_optionale>div.stm_add_new_inner>input').value = '{}'".format(output['scraped_boat_type']))
			self.driver.execute_script("document.querySelector('div#butterbean-control-boat-type>div.stm-multiselect-wrapper>div.stm_add_new_optionale>div.stm_add_new_inner>i').click()")
			sleep(1)		
			self.driver.execute_script("document.querySelector('div#butterbean-control-captained>div.stm-multiselect-wrapper>div.stm_add_new_optionale>div.stm_add_new_inner>input').value = '{}'".format(output['scraped_captained_bareboat']))
			self.driver.execute_script("document.querySelector('div#butterbean-control-captained>div.stm-multiselect-wrapper>div.stm_add_new_optionale>div.stm_add_new_inner>i').click()")
			sleep(1)
			self.driver.execute_script("document.querySelector('div#butterbean-control-people>div.stm-multiselect-wrapper>div.stm_add_new_optionale>div.stm_add_new_inner>input').value = '{}'".format(output['scraped_people']))
			self.driver.execute_script("document.querySelector('div#butterbean-control-people>div.stm-multiselect-wrapper>div.stm_add_new_optionale>div.stm_add_new_inner>i').click()")
			sleep(1)
			self.driver.execute_script("document.querySelector('div#butterbean-control-length>label>input.widefat').value = '{}'".format(output['scraped_length']))
			self.driver.execute_script("document.querySelector('div#butterbean-control-year-built>label>input.widefat').value = '{}'".format(output['scraped_built_year']))
			self.driver.execute_script("document.querySelectorAll('div#butterbean-manager-stm_car_manager>ul>li>a')[3].click()")
			sleep(1)
			self.driver.execute_script("document.querySelector('div#butterbean-control-price>label>input.widefat').value ='{}'".format(output['scraped_everyday_price']))
			self.driver.execute_script("document.querySelector('div#butterbean-control-regular_price_label>label>input.widefat').value ='{}'".format('Per day'))
			self.driver.execute_script("document.querySelector('div#butterbean-control-regular_price_description>label>input.widefat').value ='${} /d(7+ days)'".format(output['scraped_over_sevenday_price']))
			self.driver.execute_script("document.querySelectorAll('div#butterbean-manager-stm_car_manager>ul>li>a')[5].click()")
			sleep(1)
			self.driver.execute_script("document.querySelector('div#butterbean-control-gallery>p>button.butterbean-add-media').click()")
			sleep(2)
			i = 0
			for image in output['scraped_gallery']:
				if i != 0:
					self.driver.execute_script("document.querySelector('div#butterbean-control-gallery>p>button.butterbean-change-media').click()")
					sleep(2)
				self.driver.execute_script("document.querySelectorAll('div.media-router>a.media-menu-item')[0].click()")
				sleep(1)
				self.driver.execute_script("document.querySelector('button#em-external-link').click()")
				sleep(1)
				self.driver.execute_script("document.querySelector('input#url').value = '{}'".format(image))
				sleep(1)
				self.driver.execute_script("document.querySelector('input#el-insert').click()")
				sleep(4)
				self.driver.execute_script("document.querySelectorAll('div.thumbnail')[0].click()")
				self.driver.execute_script("document.querySelector('div.media-toolbar-primary>button.media-button-select').click()")
				sleep(2)
				i+=1
		except Exception as e:
			print('Exception from: listing_manager',e)
			pass
	
	def listings_info(self,output):
		try:
			'''
			listings = self.driver.execute_script("document.querySelector('div#acf_2121').getAttribute('class')").split()
			if len(listings) == 4:
				self.driver.execute_script("document.querySelector('div#acf_2121>button').click()")
				sleep(1)
			self.driver.execute_script("document.querySelector('textarea#acf-field-description').value = '{}'".format(output['scraped_description']))
			info_id = self.driver.execute_script("document.querySelectorAll('div#acf-infos>div>div')[1].querySelector('textarea.wp-editor-area').getAttribute('id')")
			self.driver.execute_script("tinyMCE.EditorManager.get('{}').setContent('{}')".format(info_id,output['scraped_boat_info']))
			spec_id = self.driver.execute_script("document.querySelectorAll('div#acf-specifications>div>div')[1].querySelector('textarea.wp-editor-area').getAttribute('id')")
			self.driver.execute_script("tinyMCE.EditorManager.get('{}').setContent('{}')".format(spec_id,output['scraped_boat_specification']))
			add_id = self.driver.execute_script("document.querySelectorAll('div#acf-additionals>div>div')[1].querySelector('textarea.wp-editor-area').getAttribute('id')")
			self.driver.execute_script("tinyMCE.EditorManager.get('{}').setContent('{}')".format(add_id,output['scraped_daily_additional_charges']))
			'''
			self.driver.find_element_by_xpath("//textarea[@id='acf-field-description']").send_keys(output['scraped_description'])#description
			sleep(1)
			self.driver.execute_script("window.scrollBy(0,300)")
			sleep(2)
			raw_info_id = self.driver.find_element_by_xpath("//div[@id='acf-infos']//div//div[2]//textarea[@class='wp-editor-area']")
			info_id = raw_info_id.get_attribute("id")
			str_info_id = str("javascript:tinyMCE.EditorManager.get('"+info_id+"').setContent('"+output['scraped_boat_info']+"')")#infos
			self.driver.execute_script(str_info_id)
			sleep(1)
			self.driver.execute_script("window.scrollBy(0,300)")
			sleep(2)
			raw_spec_id = self.driver.find_element_by_xpath("//div[@id='acf-specifications']//div//div[2]//textarea[@class='wp-editor-area']")
			spec_id = raw_spec_id.get_attribute("id")
			str_spec_id = str("javascript:tinyMCE.EditorManager.get('"+spec_id+"').setContent('"+output['scraped_boat_specification']+"')")#specs
			self.driver.execute_script(str_spec_id)
			sleep(1)
			self.driver.execute_script("window.scrollBy(0,300)")
			sleep(2)
			raw_add_id = self.driver.find_element_by_xpath("//div[@id='acf-additionals']//div//div[2]//textarea[@class='wp-editor-area']")
			add_id = raw_add_id.get_attribute("id")
			str_add_id = str("javascript:tinyMCE.EditorManager.get('"+add_id+"').setContent('"+output['scraped_daily_additional_charges']+" "+output['scraped_additional_amenities']+"')")#additionals
			self.driver.execute_script(str_add_id)

			self.driver.execute_script("document.querySelector('input#acf-field-second_price').value = '{}'".format(output['scraped_over_sevenday_price']))
			self.driver.execute_script("document.querySelector('input#acf-field-captain_service').value = '{}'".format(output['scraped_captain_service']))
			self.driver.execute_script("document.querySelector('input#acf-field-damage_deposit').value = '{}'".format(output['scraped_damage_deposite']))
			self.driver.execute_script("document.querySelector('input#acf-field-fuel_expenses').value = '{}'".format(output['scraped_fuel_expenses']))

			self.driver.execute_script("document.querySelector('input#acf-field-captain_name').value = '{}'".format(output['scraped_captain_name']))
			self.driver.execute_script("document.querySelector('input#acf-field-captain_image').value = '{}'".format(output['scraped_captain_image']))

		except Exception as e:
			print('Exception from: listings_info',e)
			pass

	def post_new_listings(self,output):
		try:
			self.get_page(self.add_new_listings)
			self.title(output)
			self.backend_editor_mapping(output)
			self.listing_manager(output)
			self.listings_info(output)
			self.driver.execute_script("document.querySelector('table.form-table>tbody>tr.stm_admin_title>td>select.has-value' ).options[1].selected = 'selected'")
			sleep(1)
			self.driver.execute_script("document.querySelector('div#publishing-action>input#publish').click()")
		except Exception as e:
			print('Exception from: post_new_listings',e)
			pass	

	def strart_up(self):
		try:
			self.start_driver()
			self.get_page(self.wp_admin)
			self.login()
		except Exception as e:
			print('Exception from: strart_up',e)
			pass

	def ending(self):
		try:
		    self.close_driver()	
		except Exception as e:
			print('Exception from: ending',e)
			pass
