import librosa
import numpy as np
import os, time, time, struct, datetime
import pyaudiowpatch as pyaudio
from pythonosc import udp_client
from porcupine import Porcupine
from porcupine_util import LIBRARY_PATH, MODEL_FILE_PATH, KEYWORD_FILE_PATHS, KEYWORDS
#import pvporcupine # Needs access_key...

# Change OSC Target port here from the default 9000 as needed
client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

# Keywords to react to
keywords = ["americano", "terminator"]
keyword_sensitivity = [0.5, 0.5]  # Adjust per keyword as needed

assert len(keywords) == len(
	keyword_sensitivity
), "You changed something wrong. Each keyword in 'keywords' needs a 'keyword_sensitivity' value and the other way around..."

if all(x in KEYWORDS for x in keywords):
	keyword_file_paths = [KEYWORD_FILE_PATHS[x] for x in keywords]
else:
	raise ValueError('Acceptable keywords: %s' % ', '.join(KEYWORDS))

keyword_names = list()
for x in keyword_file_paths:
	keyword_names.append(
		os.path.basename(x).replace('.ppn', '').replace('_compressed',
														'').split('_')[0])

print('\nListening for:')
for keyword_name, sensitivity in zip(keyword_names, keyword_sensitivity):
	print(' - %s (keyword sensitivity: %.2f)' % (keyword_name, sensitivity))

porcupine = None
pa = None
audio_stream = None

porcupine = Porcupine(library_path=LIBRARY_PATH,
					  model_file_path=MODEL_FILE_PATH,
					  keyword_file_paths=keyword_file_paths,
					  sensitivities=keyword_sensitivity)

pa = pyaudio.PyAudio()

wasapi_info = pa.get_host_api_info_by_type(pyaudio.paWASAPI)

default_speakers = pa.get_device_info_by_index(
	wasapi_info["defaultOutputDevice"])

if not default_speakers["isLoopbackDevice"]:
	for loopback in pa.get_loopback_device_info_generator():
		if default_speakers["name"] in loopback["name"]:
			default_speakers = loopback
			break

print(
	f"\nRecording from: ({default_speakers['index']}){default_speakers['name']}: {default_speakers}\n"
)

INPUT_CHANNELS = int(default_speakers["maxInputChannels"])
INPUT_SAMPLE_RATE = int(default_speakers["defaultSampleRate"])
INPUT_CHUNK = int(INPUT_SAMPLE_RATE)
SAMPLE_RATE = porcupine.sample_rate
CHUNK = int(SAMPLE_RATE)

CORRECTION = int(INPUT_SAMPLE_RATE / SAMPLE_RATE)

audio_stream = pa.open(
	format=pyaudio.paInt16,
	channels=INPUT_CHANNELS,
	rate=INPUT_SAMPLE_RATE,
	input=True,
	input_device_index=default_speakers["index"],
	frames_per_buffer=porcupine.frame_length * CORRECTION,
)

#output=open("test.raw","wb")

STRUCT_SIZE = struct.calcsize("h" * porcupine.frame_length)
printed_ready = False
while True:
	input_data = audio_stream.read(porcupine.frame_length * CORRECTION,
								   exception_on_overflow=True)

	floats = librosa.util.buf_to_float(input_data, n_bytes=2, dtype=np.float32)

	floats = np.reshape(floats, (INPUT_CHANNELS, -1), order='F')
	floats = librosa.to_mono(floats)

	audio = librosa.resample(floats,
							 orig_sr=INPUT_SAMPLE_RATE,
							 target_sr=SAMPLE_RATE)

	ints = (audio * 32767).astype(np.int16)
	pcm = ints.astype('h').tobytes()
	#output.write(pcm)
	#assert len(pcm)==STRUCT_SIZE
	pcm_porcupined = struct.unpack_from("h" * porcupine.frame_length, pcm)

	#assert len(pcm_porcupined)==porcupine.frame_length,"frame length needs to be correct"

	result = porcupine.process(pcm_porcupined)
	if not printed_ready:
		printed_ready = True
		print("Listening...")	
		
	if result >= 0:
		name = keyword_names[result]
		print('[%s] detected: %s' % (str(datetime.datetime.now()), name))

		# Change avatar parameter/keyword order here.
		if name == "terminator":
			client.send_message("/avatar/parameters/fire_effect", False)
		elif name == "americano":
			client.send_message("/avatar/parameters/fire_effect", True)
		else:
			raise ValueError("Unhandled keyword: %s"%(name,))