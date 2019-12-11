##Grocy Py Scanner
This awesome script will allow you the user to add/remove items from the system with just a barcode scanner

The script requires that you edit a few of the variables at the top of the description

UPC_DATABASE_API='UPC_API'

buycott_token='BUYCOTT_API'

GROCY_API='GROCY_API'

This is some arbitrary number.  We used a barcode generator and put in some random 7 digit number to use as our ADDID.  You could use a barcode off of something that you will never inventory

add_id='ADDID'

This is the URL of your grocy app or IP address.

base_url = 'YOUR_GROCY_URL'

This is where you want the product to go.  I created an entry ADDED_UPDATE_LOCATION so that it stands out when going through the prduct list so I know it needs to be addressed.

This could be enhanced with barcodes that represent each location you have, then have the main function do some stuff but eh not worth it for me at this time.

This can be found by clicking on the location in the app and looking at the URL of course if you're curl savvy you could always query the api directly.

location_id = LOCATION_ID

Optional

homeassistant_url='YOUR_HOME_ASSISTANT_URL/DOMAIN/SERVICE'

homeassistant_api='YOUR_HOME_ASSISTANT_API'

I wrote this because I knew there was no way I would be able to get the house on board with using this if they needed to run around with a computer with the scanner attached to it.

So instead I plugged the dongle for my scanner into a raspberry pi that runs my sprinklers and I just run the app from there.  Right now I run it in a screen session so that I can see the output.  

I'm working on coming up with some sort of a solution to let the user know if the scan worked.  Right now best idea I have come up with is to make another API call to my HomeAssistant and then have HomeAssistant do something that informs the user that it worked.

##How To Use This
Put this script on whatever machine you want.  Your local laptop, raspberry pi it doesn't matter just as long as wherever you put it, is the same place as your barcode scanner.  In my case its on my raspberry pi that is running OpenSprinkler because 9 months out of the year that pi is just sitting idle.  It doesn't matter where you run this script from though as long as it can make the necessary API calls that it needs to do.  If you want to run it on the same machine that you have grocy thats cool too.  In my case Grocy is on my docker VM so that was not an option for me hence why I put it on the pi.  YMMV.  If you have any questions please let me know.

Once you have the script installed just execute it with ./barcode_reader.py I don't have it setup to do logging so it will just print everything to the screen which is handy so you can see what its doing.  I'll probably implement logging down the road though.  If you don't want to see what its doing just add a & to the end of the command like ./barcode_reader.py & 

##Update:

04/29/2019: I got the home assistant integration working.  For me I have this going to an Echo that is in my kitchen and I have it speak what mode it is in and if I added something it tells me how many it added it by.  If this is the first time addding it will say zero because the quantity hasn't been setup properly in the database yet.  Once you update the system to the correct quantity for the item then it will work just fine.

The Text To Speech is a little delayed because well it has to make the call to HomeAssistant which in turn has to make the call to convert the Text To Speech to whatever you have playing it.  

I am fully open to pull requests as I am certain there are enhancements that someone who is a little more python savvy than myself could come up with or perhaps optimize the code a little more

Right now when its adding you need to let it chunk through that bit before scanning.  Once everything is added to the system and its just doing increase/decrease operations you can scan pretty fast because its all local calls.

I have buycott in there because they allow you to have 7 days free before they bill you for the service.  I'll probably be changing the order of the services but haven't decided yet.

12/11/2019:  Did a lot of code optimization in here to try and clean things up.  Also had to put in some error handling for Wal-Mart because they're returning what python says is invalid json so instead of the script puking and dying it now handles the error and keeps moving along.

Enjoy!
