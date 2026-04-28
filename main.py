import json
import subprocess
import wave
import array


import audioop
import datetime
import pyaudiowpatch as pyaudio
from pythonosc import udp_client
import pvporcupine


def load_config(config_path="config.json"):
	with open(config_path, "r") as f:
		return json.load(f)


def setup_porcupine(config):
	keywords = list(config["keywords"].keys())
	keyword_sensitivity = [config["keywords"][k]["sensitivity"] for k in keywords]

	print("\nListening for:")
	for keyword_name, sensitivity in zip(keywords, keyword_sensitivity):
		print(" - %s (keyword sensitivity: %.2f)" % (keyword_name, sensitivity))

	_keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in keywords]

	porcupine = pvporcupine.create(
		library_path=pvporcupine.LIBRARY_PATH,
		model_path=pvporcupine.MODEL_PATH,
		keyword_paths=_keyword_paths,
		sensitivities=keyword_sensitivity,
	)

	return porcupine, keywords, keyword_sensitivity


def init(config, client):
	porcupine, keywords, _ = setup_porcupine(config)

	pa = pyaudio.PyAudio()

	wasapi_info = pa.get_host_api_info_by_type(pyaudio.paWASAPI)

	default_speakers = pa.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

	if not default_speakers["isLoopbackDevice"]:
		for loopback in pa.get_loopback_device_info_generator():
			if default_speakers["name"] in loopback["name"]:
				default_speakers = loopback
				break

	print(
		f"\nRecording from: ({default_speakers['index']}){default_speakers['name']}\n"
	)

	INPUT_CHANNELS = int(default_speakers["maxInputChannels"])
	INPUT_SAMPLE_RATE = int(default_speakers["defaultSampleRate"])
	TARGET_SAMPLE_RATE = porcupine.sample_rate
	TARGET_FRAME_LENGTH = porcupine.frame_length
	frame_sz = TARGET_FRAME_LENGTH * int(INPUT_SAMPLE_RATE / TARGET_SAMPLE_RATE)
	data_format = pyaudio.paInt16
	audio_stream = pa.open(
		format=data_format,
		channels=INPUT_CHANNELS,
		rate=INPUT_SAMPLE_RATE,
		input=True,
		input_device_index=default_speakers["index"],
		frames_per_buffer=frame_sz,
	)
	SAMPLE_SIZE = pa.get_sample_size(data_format)
	printed_ready = False

	waveFile = wave.open("out.wav", "wb")
	waveFile.setnchannels(1)
	waveFile.setsampwidth(SAMPLE_SIZE)
	waveFile.setframerate(TARGET_SAMPLE_RATE)
	recorded = []
	wrong_sized_events = 0
	frame_n = 0
	resample_state = None
	try:
		while True:
			try:
				input_data = audio_stream.read(frame_sz, exception_on_overflow=True)
			except OSError as e:
				try:
					audio_stream.close()
					pa.terminate()
				except Exception as _e:
					print(_e)
				print(e)
				return

			# Convert to mono by averaging channels (assuming 2 channels)
			if INPUT_CHANNELS > 2:
				raise RuntimeError("TODO")
			elif INPUT_CHANNELS == 2:
				mono_data = audioop.tomono(input_data, SAMPLE_SIZE, 0.5, 0.5)
			else:
				mono_data = input_data

			# Resample using audioop.ratecv, preserve state for streaming
			resampled_data, resample_state = audioop.ratecv(
				mono_data,
				SAMPLE_SIZE,
				1,
				INPUT_SAMPLE_RATE,
				TARGET_SAMPLE_RATE,
				resample_state,
			)

			# Convert bytes to int16 samples for porcupine
			pcm_samples = array.array("h", resampled_data)
			# Take only the expected number of samples, this appears to be fine?
			pcm_samples = pcm_samples[:TARGET_FRAME_LENGTH]
			# Convert back to bytes for recording
			pcm_porcupined = pcm_samples.tobytes()

			recorded_frame_size = len(pcm_samples)

			if recorded_frame_size == 0:
				continue

			if recorded_frame_size != TARGET_FRAME_LENGTH:
				wrong_sized_events += 1
				if wrong_sized_events > 2:
					print("recorded_frame_size", recorded_frame_size)
					raise RuntimeError("Size wrong. Programming error.")
				continue
			if frame_n < 256:
				frame_n += 1
				assert recorded is not None
				recorded.append(pcm_porcupined)
				if frame_n == 256:
					assert waveFile and recorded
					waveFile.writeframes(b"".join(recorded))
					waveFile.close()
					recorded = None
					waveFile = None
					print("debug dumped audio to out.wav")

			result = porcupine.process(pcm_samples)
			if not printed_ready:
				printed_ready = True
				print("Listening...")

			if result >= 0:
				name = keywords[result]
				print(
					"[%s] detected: %s"
					% (
						str(
							datetime.datetime.now().isoformat(
								sep=" ", timespec="seconds"
							)
						),
						name,
					)
				)

				for address, value in config["keywords"][name]["triggers"].items():
					client.send_message(address, value)

				if "commands" in config["keywords"][name]:
					for cmd in config["keywords"][name]["commands"]:
						subprocess.run(cmd, shell=True)
	except KeyboardInterrupt:
		pass
	finally:
		try:
			if audio_stream:
				audio_stream.close()
			if pa:
				pa.terminate()
			if waveFile:
				waveFile.close()
			porcupine.delete()
		except Exception as e:
			print(e)


def main():
	config = load_config()
	client = udp_client.SimpleUDPClient(config["osc"]["host"], config["osc"]["port"])
	init(config, client)


if __name__ == "__main__":
	main()
