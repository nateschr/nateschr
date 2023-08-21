from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import selenium
import time
import requests
import os

service = Service(executable_path='chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument('--headless=new')
options.add_argument("--mute-audio")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

invalid_char = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
downloaded_files = os.listdir("E:\\Python Projects\\CBB Downloader")

driver.get("https://castbox.fm/channel/id5493704?utm_campaign=web_amp_view_all&utm_medium=dlink&utm_source=web_amp&utm_content=cid_5493704&country=us")
original_window = driver.current_window_handle

# get master list
master_list_elem = driver.find_elements('xpath', '//*[@id="trackListCon_list"]/div')
scroll_num = 201
for i in range(scroll_num):
	body = driver.find_element('xpath', '/html/body')
	body.send_keys(Keys.PAGE_DOWN)
	time.sleep(0.1)
	print('Caching episodes..','(',i,')','(',scroll_num,')')

# iterate through list
for n in range(1, 882):
	time.sleep(0.5)

	try:
		element = WebDriverWait(driver, 60).until(
		EC.presence_of_element_located((By.ID, 'trackListCon_list')))
	except selenium.common.exceptions.TimeoutException:
		print('Exception: could not find element "trackListCon_list", attempting to continue anyway...')
		pass
	item_text = driver.find_element('xpath', str('//*[@id="trackListCon_list"]/div/section[') + str(n) + str(']/div[1]/div[2]/a/p'))
	item_title = item_text.get_attribute('title')
	title_clean = ''.join(x for x in item_title if not x in invalid_char)

	# If we haven't already downloaded, go to episode page
	if (title_clean + str('.mp3')) not in downloaded_files:
		item_link = driver.find_element('xpath', str('//*[@id="trackListCon_list"]/div/section[') + str(n) + str(']/div[1]/div[2]/a'))
		item_link = item_link.get_attribute('href')
		#####driver.get(item_link)
		print('Navigating to', item_link)
		driver.execute_script('window.open("' + str(item_link) + '");')

		# get the handle of the new, recently opened tab
		new_window = driver.window_handles[1]
		orig_window = driver.window_handles[0]
		# switch to the recently opened tab
		driver.switch_to.window(window_name=new_window)

		# Loads episode page, wait until necessary elements show up
		element = WebDriverWait(driver, 20).until(
		EC.presence_of_element_located((By.ID, 'root')))
		element = WebDriverWait(driver, 20).until(
		EC.presence_of_element_located((By.ID, 'childrenBox')))

		# Grab episode title, sanitize
		mp3_title = driver.find_element('xpath', "//*[@id='childrenBox']/div[4]/div[1]/span[3]/span")
		mp3_title = mp3_title.text
		mp3_title = ''.join(x for x in mp3_title if not x in invalid_char)

		# Get MP3 link
		mp3_elem = driver.find_element('xpath', "//*[@id='root']/div/div[1]/audio/source")
		mp3_link = mp3_elem.get_attribute('src')
		driver.get(mp3_link)
		print('Downloading: ', mp3_title)

		# Download MP3
		doc = requests.get(mp3_link)
		with open(str(mp3_title) + str('.mp3'), 'wb') as f:
			f.write(doc.content)
		print('Downloaded.\n')
		driver.close()
		driver.switch_to.window(window_name=orig_window)

		# Go back 2 pages to master list
		###driver.execute_script("window.history.go(-2)")
	else:
		print('File ', item_title, ' already downloaded. Skipping...')
		continue
