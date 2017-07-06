# EverwingHax

I add a release, v1.0 - This includes a python executable that you can use without worrying about if you have the right version of python or anything else. Just click and run.

## WRITTEN IN PYTHON 2.7.13 ##

You can also download the release of the .EXE here (https://github.com/IPFR33LY/EverwingHax/releases)

Download both Everwing_data.py and p3lzstring.py
place both into the same folder.

Once done, you can run Everwing_data.py and follow the screen prompts.

You can get your UID by looking for https://wintermute-151001.appspot.com/game/ in the network log when hitting F12, with the Everwing Game open. It should be in the JSON response from their server.

If you make any modifications to the way the Game State String is encoded and sent, you will end up causing a DoS to yourself and will not be able to play the game until a new Game State is submitted with properly encoding.

Everwing_data.py will create a 'statefile.txt' document after its first initial run. This file contains your entire Game State.




******************************************
MIT License

Copyright (c) [2017] [Andrew Anderson]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
******************************************
