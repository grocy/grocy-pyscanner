#!/usr/bin/python
import signal, sys
import json
import requests

from evdev import InputDevice, categorize, ecodes

#This will allow you to work the grocy inventory with a barcode scanner
#I found I needed to just declare some things right off the bat when the app loads such as the ADD and barcode
UPC_DATABASE_API=''
#I've been waiting for my token but you can register for one at developers.walmart.com
walmart_token=''
#This UPC lookup doesn't require a token or anything
walmart_search=1
#This UPC DB also doesn't require a token but does have a limit of 100 calls per day
upc_item_db=1
#Your Grocy API Key
GROCY_API=''
#This is some arbitrary number.  We used a barcode generator and put in some random 7 digit number to use as our ADDID.  You could use a barcode off of something that you will never inventory
add_id='43235735'
#This is the URL of your grocy app or IP address.
base_url = 'http://grocy.thefuzz4.net/api'
ADD = 0
barcode = ''
message_text = ''
#This is where you want the product to go.  I created an entry ADDED_UPDATE_LOCATION so that it stands out when going through the prduct list so I know it needs to be addressed.
#This could be enhanced with barcodes that represent each location you have, then have the main function do some stuff but eh not worth it for me at this time
location_id = 6
device = InputDevice('/dev/input/event0') # Replace with your device
scancodes = {
	11:	u'0',
	2:	u'1',
	3:	u'2',
	4:	u'3',
	5:	u'4',
	6:	u'5',
	7:	u'6',
	8:	u'7',
	9:	u'8',
	10:	u'9'
}
NOT_RECOGNIZED_KEY = u'X'
homeassistant_url='YOUR_HOME_ASSISTANT_URL/DOMAIN/SERVICE'
homeassistant_api='YOUR_HOME_ASSISTANT_API'

def increase_inventory(upc):
	global response_code
	global product_name
	#Need to lookup our product_id, if we don't find one we'll do a search and add it
	product_id_lookup(upc)
	print ("Increasing %s") % (product_name)
	url = base_url+"/stock/products/%s/add" % (product_id)
	data = {'amount': purchase_amount,
	    'transaction_type': 'purchase'}
	#We have everything we need now in order to complete the rest of this function
	grocy_api_call_post(url, data)
	#As long as we get a 200 back from the app it means that everything went off without a hitch
	if response_code != 200:
	    print ("Increasing the value of %s failed") % (product_name)
	else:
	  if homeassistant_token != '':
	    product_id_lookup(upc)
	    message_text="I increased %s by a count of %s to a total count of %s" % (product_name, purchase_amount, stock_amount)
	    homeassistant_call(message_text)
	barcode = ''

def decrease_inventory(upc):
	global response_code
	#Going to see if we can find a product_id, if we don't find it we'll add it.  Problem here though is that we need to have a quantity in the system.  If there isn't any we'll error because there is nothing to decrease.  This is ok
	product_id_lookup(upc)
	print("Stepping into the decrease")
	#Lets make sure we can actually decrease this before we get too crazy
	if stock_amount > 0:
		print ("Decreasing %s by 1") % (product_name)
		url = base_url+"/stock/products/%s/consume" % (product_id)
		data = {'amount': 1,
	        'transaction_type': 'consume',
	        'spoiled': 'false'}
		#We now have everything we need and we can now proceed
		grocy_api_call_post(url, data)
		if response_code == 400:
			print ("Decreasing the value of %s failed, are you sure that there was something for us to decrease?") % (product_name)
			message_text=("I failed to decrease %s, please try again") % (product_name)
			homeassistant_call(message_text)
	else:
		print ("The current stock amount for %s is 0 so there was nothing for us to do here") % (product_name)
		if homeassistant_token != '':
			message_text=("There was nothing for me to decrease for %s so we did nothing") % (product_name)
			homeassistant_call(message_text)
	if homeassistant_token != '':
		product_id_lookup(upc)
		message_text=("Consumed %s.  You now have %s left") % (product_name, stock_amount)
		homeassistant_call(message_text)
	barcode=''

def product_id_lookup(upc):
	#Need to declare this as a global and we'll do this again with a few others because we need them elsewhere
	global product_id
	print("Looking up the product_id")
	#Lets check to see if the UPC exists in grocy
	url = base_url+"/stock/products/by-barcode/%s" % (upc)
	headers = {
	'cache-control': "no-cache",
	'GROCY-API-KEY': GROCY_API
	}
	r = requests.get(url, headers=headers)
	r.status_code
	print (r.status_code)
	#Going to check and make sure that we found a product to use.  If we didn't find it lets search the internets and see if we can find it.
	if r.status_code == 400:
		message_text=("I did not have the product locally so I am now going to search for it and add it to the system")
		if homeassistant_token != '':
			homeassistant_call(message_text)
		upc_lookup(upc)
	else:
		j = r.json()
		global product_id
		product_id = j['product']['id']
		global purchase_amount
		purchase_amount = j['product']['qu_factor_purchase_to_stock']
		global product_name
		product_name = j['product']['name']
		print ("Our product_id is %s") % (product_id)
		global stock_amount
		stock_amount = j['stock_amount']

def upc_lookup(upc):
	found_it=0
	if UPC_DATABASE_API != '' and found_it == 0:
		print("Looking up the UPC")
		url = "https://api.upcdatabase.org/product/%s/%s" % (upc, UPC_DATABASE_API)
		headers = {
		'cache-control': 'no-cache'
		}
		try:
			r = requests.get(url, headers=headers)
			if r.status_code==200:
				print("UPC DB found it so now going to add it to the system")
				j = r.json()
				name = j['title']
				description = j['description']
				#We now have what we need to add it to grocy so lets do that
				add_to_system(upc, name, description)
				found_it=1
		except requests.exceptions.Timeout:
			print("The connection timed out")
		except requests.exceptions.TooManyRedirects:
			print ("Too many redirects")
		except requests.exceptions.RequestException as e:
			print (e)
	if walmart_search == 1 and found_it==0:
		print("Looking up in Wal-Mart Search")
		url = "https://search.mobile.walmart.com/v1/products-by-code/UPC/%s?storeId=1" % (upc)
		headers = {
		'Content-Type': 'application/json',
		'cache-control': "no-cache"
		}
		try:
			r = requests.get(url=url, headers=headers)
			j = r.json()
			if r.status_code == 200:
				print("Walmart Search found it so now we're going to gather some info here and then add it to the system")
				if 'data' in j:
					name = j['data']['common']['name']
					description = ''
					#We now have what we need to add it to grocy so lets do that
					#Sometimes buycott returns a success but it never actually does anything so lets just make sure that we have something
					add_to_system(upc, name, description)
					found_it=1
		except requests.exceptions.Timeout:
			print("The connection timed out")
		except requests.exceptions.TooManyRedirects:
			print ("Too many redirects")
		except requests.exceptions.RequestException as e:
			print (e)
	if upc_item_db == 1 and found_it==0:
		#This is a free service that limits you to 100 hits per day if we can't find it here we'll still create it in the system but it will be just a dummy entry
		print("Looking up in UPCItemDB")
		url = "https://api.upcitemdb.com/prod/trial/lookup?upc=%s" % (upc)
		headers = {
		'Content-Type': 'application/json',
		'cache-control': "no-cache"
		}
		try:
			r = requests.get(url=url, headers=headers)
			j = r.json()
			if r.status_code == 200:
				if 'total' in j:
					total = j['total']
					if total != 0:
						print("UPCItemDB found it so now we're going to gather some info here and then add it to the system")
						name=j['items'][0]['title']
						description = j['items'][0]['description']
						#We now have what we need to add it to grocy so lets do that
						add_to_system(upc, name, description)
						found_it=1
		except requests.exceptions.Timeout:
			print("The connection timed out")
		except requests.exceptions.TooManyRedirects:
			print ("Too many redirects")
		except requests.exceptions.RequestException as e:
			print (e)
	if ean_data_db == 1 and found_it==0:
		#This is a free service that limits you to 100 hits per day if we can't find it here we'll still create it in the system but it will be just a dummy entry
		print("Looking up in EANDB")
		url = "https://eandata.com/feed/?v=3&keycode=%s&mode=json&find=011110018427" % (ean_data_db, upc)
		headers = {
		'Content-Type': 'application/json',
		'cache-control': "no-cache"
		}
		try:
			r = requests.get(url=url, headers=headers)
			j = r.json()
			if r.status_code == 200:
				if 'product' in j:
					total = j['total']
					if total != 0:
						print("UPCItemDB found it so now we're going to gather some info here and then add it to the system")
						name = j['product'][0]['attributes']['product']
						description=''
						#We now have what we need to add it to grocy so lets do that
						add_to_system(upc, name, description)
						found_it=1
		except requests.exceptions.Timeout:
			print("The connection timed out")
		except requests.exceptions.TooManyRedirects:
			print ("Too many redirects")
		except requests.exceptions.RequestException as e:
			print (e)
	if found_it==0:
		print ("The item with %s was not found so we're adding a dummy one") % (upc)
		name="The product was not found in the external sources you will need to fix %s" % (upc)
		description='dummy'
		add_to_system(upc, name, description)
		found_it=1
		if found_it==1:
			#By now we have our product added to the system.  We can now lookup our product_id again and then proceed with whatever it is we were doing
			product_id_lookup(upc)
		else:
			message_text=("I was unable to find a productID for %s and it is not in the system")
			homeassistant_call(message_text)
			print(message_text)

#Rather than have this in every section of the UPC lookup we just have a function that we call for building the json for the api call to actually add it to the system
def add_to_system(upc, name, description):
	url = base_url+"/objects/products"
	data ={"name": name,
		"description": description,
		"barcode": upc,
		"location_id": location_id,
		"qu_id_purchase": 1,
		"qu_id_stock":0,
		"qu_factor_purchase_to_stock": 1,
		"default_best_before_days": -1
		}
	grocy_api_call_post(url, data)
	if response_code==204:
		print("Just added %s to the system") % (name)
		product_id_lookup(upc)
	else:
		print("Adding the product with %s failed") % (upc)

#This is a function that is referred to a lot through out the app so its easier for us to just use it as a function rather than type it out over and over
def grocy_api_call_post(url, data):
	headers = {
		'cache-control': "no-cache",
		'GROCY-API-KEY': GROCY_API
		}
	try:
		r = requests.post(url=url, json=data, headers=headers)
		r.status_code
		global response_code
		response_code = r.status_code
		print (r.status_code)
	except requests.exceptions.Timeout:
		print("The connection timed out")
	except requests.exceptions.TooManyRedirects:
		print ("Too many redirects")
	except requests.exceptions.RequestException as e:
		print (e)

def homeassistant_call(message_text):
	print("Calling homeassistant to speak some text")
	headers = {
	'Authorization': 'Bearer {}'.format(homeassistant_token),
	'Content-Type': 'application/json'
	}
	data = { "entity_id": "media_player.jason_s_2nd_echo_show_2",
	"message": message_text
	}
	r = requests.post(url=homeassistant_url, json=data, headers=headers)
	r.status_code
	if r.status_code != 200:
		print("HomeAssistant call failed with a status code of %s") % (r.status_code)

def make_auth_token(upc_string, auth_key):
	global signature
	sha_hash = hmac.new(auth_key, upc_string, hashlib.sha1)
	signature = base64.b64encode(sha_hash.digest()).decode()
	print (signature)

for event in device.read_loop():
	if event.type == ecodes.EV_KEY:
		eventdata = categorize(event)
		if eventdata.keystate == 1: # Keydown
			scancode = eventdata.scancode
			if scancode == 28: # Enter
				print (barcode)
				if barcode != '' and len(barcode) >= 7:
					if barcode == add_id and ADD == 0:
						ADD = 1
						barcode=''
						print("Entering add mode")
						if homeassistant_token != '':
							message_text="Entering add mode"
							homeassistant_call(message_text)
					elif barcode == add_id and ADD == 1:
						ADD = 0
						barcode=''
						print("Entering consume mode")
						if homeassistant_token != '':
							message_text="Entering consume mode"
							homeassistant_call(message_text)
					elif ADD == 1:
						upc=barcode
						barcode=''
						increase_inventory(upc)
					elif ADD == 0:
						upc=barcode
						barcode=''
						decrease_inventory(upc)

			else:
				key = scancodes.get(scancode, NOT_RECOGNIZED_KEY)
				barcode = barcode + key
				if key == NOT_RECOGNIZED_KEY:
					print('unknown key, scancode=' + str(scancode))
