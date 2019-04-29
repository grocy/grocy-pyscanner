This awesome script will allow you the user to add/remove items from the system with just a barcode scanner

The script requires that you edit a few of the variables at the top of the description

UPC_DATABASE_API='UPC_API'
buycott_token='BUYCOTT_API'
GROCY_API='GROCY_API'
This is some arbitrary number.  We used a barcode generator and put in some random 7 digit number to use as our ADDID.  You could use a barcode off of something that you will never inventory
add_id='ADDID'
This is the URL of your grocy app or IP address.
base_url = 'YOUR_GROCY_URL'
ADD = 0
barcode = ''
This is where you want the product to go.  I created an entry ADDED_UPDATE_LOCATION so that it stands out when going through the prduct list so I know it needs to be addressed.
This could be enhanced with barcodes that represent each location you have, then have the main function do some stuff but eh not worth it for me at this time
This can be found by clicking on the location in the app and looking at the URL of course if you're curl savvy you could always query the api directly
location_id = LOCATION_ID
Optional
homeassistant_url='YOUR_HOME_ASSISTANT_URL/DOMAIN/SERVICE'
homeassistant_api='YOUR_HOME_ASSISTANT_API'

I wrote this because I knew there was no way I would be able to get the house on board with using this if they needed to run around with a computer with the scanner attached to it.

So instead I plugged the dongle for my scanner into a raspberry pi that runs my sprinklers and I just run the app from there.  Right now I run it in a screen session so that I can see the output.  

I'm working on coming up with some sort of a solution to let the user know if the scan worked.  Right now best idea I have come up with is to make another API call to my HomeAssistant and then have HomeAssistant do something that informs the user that it worked.

Update:

04/29/2019: I got the home assistant integration working.  For me I have this going to an Echo that is in my kitchen and I have it speak what mode it is in and if I added something it tells me how many it added it by.  If this is the first time addding it will say zero because the quantity hasn't been setup properly in the database yet.  Once you update the system to the correct quantity for the item then it will work just fine.

The Text To Speech is a little delayed because well it has to make the call to HomeAssistant which in turn has to make the call to convert the Text To Speech to whatever you have playing it.  

I am fully open to pull requests as I am certain there are enhancements that someone who is a little more python savvy than myself could come up with or perhaps optimize the code a little more

Right now when its adding you need to let it chunk through that bit before scanning.  Once everything is added to the system and its just doing increase/decrease operations you can scan pretty fast because its all local calls.

I have buycott in there because they allow you to have 7 days free before they bill you for the service.  I'll probably be changing the order of the services but haven't decided yet.

Enjoy!
