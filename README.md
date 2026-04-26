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
 - [uv](https://github.com/astral-sh/uv) installed (see below).
 - If VRChat:
    - VRChat avatar knowledge ( See: [VR Audience Fire Avatar Prefab](https://github.com/Python1320/vr_audience_fire/) for an example )
    - An avatar you have uploaded yourself or an existing OSC parameter (see how to use).
    - Some knowledge about the [OSC system](https://docs.vrchat.com/docs/osc-avatar-parameters)
 - If Garry's Mod / TF2:
    - see `config.json`, uses valvecmd.exe, windows only
    - OR programming skills in python to adapt to another game ( Source engine example in config.json )
   
### Installing uv

You need "uv" to install dependencies. See instructions [here](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2). Don't be afraid!

### How to use
  1. [Download this repository](https://github.com/Python1320/vr_audience_control/archive/refs/heads/main.zip), extract anywhere.
  
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
4. Open `config.json` and add your keyword with its triggers. Each keyword can set multiple OSC parameters:
     ```json
     "keywords": {
       "americano": {
         "sensitivity": 0.5,
         "triggers": {
           "/avatar/parameters/fire_effect": true,
           "/avatar/parameters/water_effect": false
         }
       }
     }
     ```
     To run console commands (e.g., for Source 1 games via [valvecmd](https://github.com/Python1320/valvecmd)):
     ```json
     "terminator": {
       "sensitivity": 0.5,
       "triggers": {},
       "commands": ["valvecmd.exe kill"]
     }
     ```
  5. **Optionally**: Change or add keywords
     - **Available keywords** *(Note: new picovoice that requires a license key has way more keywords to choose from. See keywords [here](https://github.com/Picovoice/porcupine/tree/master/resources))*:
        - americano
        - blueberry
        - bumblebee
        - grapefruit
        - grasshopper
        - picovoice
        - porcupine
        - terminator
  6. Launch VR **BEFORE** launching this program (This program uses the primary audio source on launch, which changes when you start VR)
  7. Launch `run.cmd` or run `uv run main.py`
  8. Ask someone to say in american accent `americano` or test with the example sound file ![example_americano_terminator.ogg](example_americano_terminator.ogg)
  9. Catch on fire or whatever 🤷


### Credits

Based on old version of https://github.com/Picovoice/porcupine/ that does not require a license key.
New version would allow using more keywords.

### TODO

 - Add [openWakeWord](https://github.com/dscripka/openWakeWord) if CPU usage is not a concern.
 - Only record the application instead of music player or similar by using https://github.com/microsoft/Windows-classic-samples/tree/main/Samples/ApplicationLoopback 
