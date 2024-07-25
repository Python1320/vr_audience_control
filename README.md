## "Voice Chat" Audience Hot Word Detection Example

Allow voice chat players/audience to control your PC with hot word detection (with minimal CPU usage).

*This example makes it so that if someone says "`americano`" in voice chat, I catch on fire 🔥 in-game.* `(American accent required)`

They can then extinguish 🧯 me by saying "`terminator`".

See example pronounciation in ![example_americano_terminator.ogg](example_americano_terminator.ogg) 

![image](https://github.com/user-attachments/assets/82877f15-2ce4-4e55-ac7d-972b66092fb3)


### Notes 

 - False positives are common so this is just a toy.
 - No warranty of any kind.

### Requirements

 - Something like 30-500MB of extra RAM (`python's fault, sorry`).
 - The program needs about 1% of CPU power with my old Intel 4th generation i7-4770.
 - [Python 3.11+](https://www.python.org/downloads/) installed.
 - VRChat avatar knowledge OR programming skills in python to adapt to another game ( Source engine example "coming soon", based on [valvecmd](https://github.com/Python1320/valvecmd) )
 - If VRChat:
    - An avatar you have uploaded yourself or an existing OSC parameter (see how to use).
    - Some knowledge about the [OSC system](https://docs.vrchat.com/docs/osc-avatar-parameters)
 - If Garry's Mod / TF2:
    - TODO
   
### How to use
 1. [Download this repository](https://github.com/Python1320/vr_audience_control/archive/refs/heads/main.zip), extract anywhere.
 2. Run `install.cmd`
 3. Open `%userprofile%\AppData\LocalLow\VRChat\VRChat\OSC` and find your Avatar based on the ID.
    - Find your avatar ID by opening https://vrchat.com/home/avatars and clicking your avatar and look at URL.
 4. [Find the boolean parameter you want to toggle on/off](https://vrc.school/docs/Avatars/Expressions-Menu-Params), in example case:  
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
 5. Open `main.py` and change the `/avatar/parameters/fire_effect` into your own boolean value.
 6. **Optionally**: Change keyword
    - **Available keywords** *(Note: new picovoice that requires a license key has way more keywords to choose from. See keywords [here](https://github.com/Picovoice/porcupine/tree/master/resources))*:
       - americano
       - blueberry
       - bumblebee
       - grapefruit
       - grasshopper
       - picovoice
       - porcupine
       - terminator
 7. Launch VR **BEFORE** launching this program (This program uses the primary audio source on launch, which changes when you start VR)
 8. Launch `run.cmd` or click `main.py`
 9. Ask someone to say in american accent `americano` or test with the example sound file ![example_americano_terminator.ogg](example_americano_terminator.ogg)
 10. Catch on fire or whatever 🤷


### Credits

Based on old version of https://github.com/Picovoice/porcupine/ that does not require a license key.
New version would allow using more keywords.

### TODO

 - Add [openWakeWord](https://github.com/dscripka/openWakeWord) if CPU usage is not a concern.
 - Only record the application instead of music player or similar by using https://github.com/microsoft/Windows-classic-samples/tree/main/Samples/ApplicationLoopback
 - Add Source 1 engine support 
