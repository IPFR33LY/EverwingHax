# EverwingHax

Download both Everwing_data.py and p3lzstring.py
place both into the same folder.

Once done, you can run Everwing_data.py and follow the screen prompts.

You can get your UID by looking for https://wintermute-151001.appspot.com/game/ in the network log when hitting F12, with the Everwing Game open. It should be in the JSON response from their server.

If you make any modifications to the way the Game State String is encoded and sent, you will end up causing a DoS to yourself and will not be able to play the game until a new Game State is submitted with properly encoding.

Everwing_data.py will create a 'statefile.txt' document after its first initial run. This file contains your entire Game State.
