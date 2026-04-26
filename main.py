import json
import subprocess
import wave

import numpy as np
import samplerate
import datetime
import pyaudiowpatch as pyaudio
from pythonosc import udp_client
import pvporcupine.util

with open("config.json", "r") as f:
    config = json.load(f)

client = udp_client.SimpleUDPClient(config["osc"]["host"], config["osc"]["port"])

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
    sensitivities=keyword_sensitivity)


def init():
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
        f"\nRecording from: ({default_speakers['index']}){default_speakers['name']}\n"
    )

    INPUT_CHANNELS = int(default_speakers["maxInputChannels"])
    INPUT_SAMPLE_RATE = int(default_speakers["defaultSampleRate"])
    TARGET_SAMPLE_RATE = porcupine.sample_rate
    TARGET_FRAME_LENGTH = porcupine.frame_length
    CORRECTION = int(INPUT_SAMPLE_RATE / TARGET_SAMPLE_RATE)
    frame_sz = TARGET_FRAME_LENGTH * CORRECTION
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

    resampler = samplerate.Resampler("sinc_fastest", channels=1)

    waveFile = wave.open("out.wav", "wb")
    waveFile.setnchannels(1)
    waveFile.setsampwidth(SAMPLE_SIZE)
    waveFile.setframerate(TARGET_SAMPLE_RATE)
    recorded = []
    wrong_sized_events = 0
    frame_n = 0
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

        frame = np.frombuffer(input_data, dtype=np.int16)\
            .reshape(-1, 2)\
            .mean(axis=1, dtype=np.float32)
        np.divide(frame, 32768.0, out=frame)

        pcm_porcupined = resampler.process(frame, TARGET_SAMPLE_RATE / INPUT_SAMPLE_RATE, end_of_input=False)

        np.multiply(pcm_porcupined, 32768.0, out=pcm_porcupined)
        pcm_porcupined = np.clip(pcm_porcupined, -32768, 32767).astype(np.int16)

        recorded_frame_size = len(pcm_porcupined)

        if not recorded_frame_size:
            continue

        if recorded_frame_size != TARGET_FRAME_LENGTH:
            wrong_sized_events += 1
            if wrong_sized_events > 2:
                print("recorded_frame_size", recorded_frame_size)
                raise ValueError("size wrong")
            continue
        if frame_n < 256:
            frame_n += 1
            assert recorded is not None
            recorded.append(pcm_porcupined.tobytes())
            if frame_n == 256:
                assert waveFile and recorded
                waveFile.writeframes(b"".join(recorded))
                waveFile.close()
                recorded = None
                waveFile = None
                print("debug dumped audio to out.wav")

        result = porcupine.process(pcm_porcupined)
        if not printed_ready:
            printed_ready = True
            print("Listening...")

        if result >= 0:
            name = keywords[result]
            print("[%s] detected: %s" % (str(datetime.datetime.now().isoformat(sep=' ', timespec='seconds')), name))

            for address, value in config["keywords"][name]["triggers"].items():
                client.send_message(address, value)

            if "commands" in config["keywords"][name]:
                for cmd in config["keywords"][name]["commands"]:
                    subprocess.run(cmd, shell=True)


def main():
    init()

if __name__ == "__main__":
    main()