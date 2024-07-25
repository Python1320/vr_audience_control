## Voice Chat Hot Word Detection example

Allow voice chat audience to control your PC with hot word detection (with minimal CPU usage).

*This example makes it so that if someone says "`americano`" with american accent in voice chat, I catch on fire in-game.* 
They can exterminate me by saying "`terminator`".
See example pronounciation in [example_americano_terminator.ogg](example_americano_terminator.ogg) 

### Notes 

 - False positives are common so this is just a toy.
 - No warranty of any kind.

### Requirements

 - Something like 30-500MB of extra RAM (python's fault, sorry).
 - App has about 1% CPU usage with my old 4th gen i7-4770.
 - [Python 3.11+](https://www.python.org/downloads/) installed.
 - VRChat or python skills to adapt to another game
 - If VRChat:
    - An avatar you have uploaded yourself or an existing OSC parameter (see how to use).
    - Some knowledge about the [OSC system](https://docs.vrchat.com/docs/osc-avatar-parameters)

### How to use
 1. Download this repository, extract anywhere.
 2. Open `%userprofile%\AppData\LocalLow\VRChat\VRChat\OSC` and find your Avatar based on the ID.
    - Find your avatar ID by opening https://vrchat.com/home/avatars and clicking your avatar and look at URL.
 3. [Find the boolean parameter you want to toggle on/off](https://vrc.school/docs/Avatars/Expressions-Menu-Params), in example case:  
    ```json
      ...
	   	{
		  	"name": "fire_effect",
		  	"input": {
					"address": "/avatar/parameters/fire_effect",
					"type": "Bool"
				  },
      ...
	```
 4. Open `main.py` and change the `/avatar/parameters/fire_effect` into your boolean value.
 5. Optionally: Find 
    - Available keywords (Note: new picovoice that requires a license key has more. See keywords [here](https://github.com/Picovoice/porcupine/tree/master/resources)):
	   - americano
       - blueberry
       - bumblebee
       - grapefruit
       - grasshopper
       - picovoice
       - porcupine
       - terminator
 6. Launch VR **BEFORE** launching this program (This program uses the primary audio source on launch, which changes when you start VR)
 7. Launch `run.cmd` or click `main.py`


### Credits

Based on old version of https://github.com/Picovoice/porcupine/ that does not require a license key.
New version would allow using more keywords.

### TODO

 - Add [openWakeWord](https://github.com/dscripka/openWakeWord) if CPU usage is not a concern.
