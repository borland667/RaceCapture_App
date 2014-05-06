RaceCapture App
===============

Next Gen version of the RaceCapture App.

Dependencies:
* Python 2.7.x
* Kivy 1.8.x
* Pyserial 2.6.x
* Graph (via kivy-garden via python-pip)

to run:

    python racecapture.py

## dev installation (OS X)

1. download [Kivy](http://kivy.org/#download) (current is 1.8.0) 
2. follow Kivy install instructions
3. install [virtualenv](http://www.virtualenv.org)
4. create a virtual environment (perhaps in this directory): `virtualenv _ve`
5. activate the virtualenv: `. _ve/bin/activate`
6. install pip requirements: `pip install -r requirements.txt`
7. install graph via garden: `garden install graph`

## running (OS X)

    /Applications/Kivy.app/Contents/Resources/script racecapture.py

## installation (Win7)

1. download [Kivy](http://kivy.org/#download) (current is 1.8.0) - remember to get the py2.7 version
2. follow Kivy install instructions
3. run kivy.bat (this adds a lot of PATH members in the current shell session)
3. Install pyserial: `pip install pyserial`
4. install graph via garden: `garden install graph`

## running (Win7)

    kivy racecapture.py
		
## dev installation (Win7)

1. Do the "installation" instructions above
1. download Eclipse (https://www.eclipse.org/downloads/)
2. At a command prompt, run kivy.bat
3. `set path`
4. Right click My Computer...System Properties...Advanced...Environment Variables...System Variables and add the extra folders that were added to the path to your system path
5. Install PyDev for Eclipse (http://pydev.org/manual_101_install.html) and use auto-config
6. (Bit hazy on this part as I tried a few things and was a bit drunk) Make a new project in Eclipse, using the folder with Racecapture in it
7. Right-click the project...Properties...pyDev-PYTHONPATH...External Libraries - in there, add kivyinstallfolder\kivy
8. Run the project