#!/usr/bin/env python

import collections
import pyaudio
import snowboydetect
import time
import wave
import os
import logging

logging.basicConfig()
logger = logging.getLogger("snowboy")
logger.setLevel(logging.INFO)
TOP_DIR = os.path.dirname(os.path.abspath(__file__))

RESOURCE_FILE = os.path.join(TOP_DIR, "resources/common.res")
DETECT_DING = os.path.join(TOP_DIR, "resources/ding.wav")
DETECT_DONG = os.path.join(TOP_DIR, "resources/dong.wav")


class RingBuffer(object):

    def __init__(self, size=4096):
        self._buf = collections.deque(maxlen=size)

    def extend(self, data):
        self._buf.extend(data)

    def get(self):
        tmp = bytes(bytearray(self._buf))
        self._buf.clear()
        return tmp


def play_audio_file(fname=DETECT_DING):
    ding_wav = wave.open(fname, 'rb')
    ding_data = ding_wav.readframes(ding_wav.getnframes())
    audio = pyaudio.PyAudio()
    stream_out = audio.open(
        format=audio.get_format_from_width(ding_wav.getsampwidth()),
        channels=ding_wav.getnchannels(),
        rate=ding_wav.getframerate(), input=False, output=True)
    stream_out.start_stream()
    stream_out.write(ding_data)
    time.sleep(0.2)
    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()


class HotwordDetector(object):

    def __init__(self, decoder_model,
                 resource=RESOURCE_FILE,
                 sensitivity=[],
                 audio_gain=1):

        tm = type(decoder_model)
        ts = type(sensitivity)
        if tm is not list:
            decoder_model = [decoder_model]
        if ts is not list:
            sensitivity = [sensitivity]
        model_str = ",".join(decoder_model)

        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=resource.encode(), model_str=model_str.encode())
        self.detector.SetAudioGain(audio_gain)
        self.num_hotwords = self.detector.NumHotwords()

        if len(decoder_model) > 1 and len(sensitivity) == 1:
            sensitivity = sensitivity * self.num_hotwords
        if len(sensitivity) != 0:
            assert self.num_hotwords == len(sensitivity), \
                "number of hotwords in decoder_model (%d) and sensitivity " \
                "(%d) does not match" % (self.num_hotwords, len(sensitivity))
        sensitivity_str = ",".join([str(t) for t in sensitivity])
        if len(sensitivity) != 0:
            self.detector.SetSensitivity(sensitivity_str.encode())

        self.ring_buffer = RingBuffer(
            self.detector.NumChannels() * self.detector.SampleRate() * 5)

    def start(self, detected_callback=play_audio_file,
              interrupt_check=lambda: False,
              sleep_time=0.03,
              audio_recorder_callback=None,
              silent_count_threshold=15,
              recording_timeout=100):
        self._running = True

        def audio_callback(in_data, frame_count, time_info, status):
            self.ring_buffer.extend(in_data)
            play_data = chr(0) * len(in_data)
            return play_data, pyaudio.paContinue

        self.audio = pyaudio.PyAudio()
        self.stream_in = self.audio.open(
            input=True, output=False,
            format=self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8),
            channels=self.detector.NumChannels(),
            rate=self.detector.SampleRate(),
            frames_per_buffer=2048,
            stream_callback=audio_callback)

        if interrupt_check():
            logger.debug("detect voice return")
            return

        tc = type(detected_callback)
        if tc is not list:
            detected_callback = [detected_callback]
        if len(detected_callback) == 1 and self.num_hotwords > 1:
            detected_callback *= self.num_hotwords

        assert self.num_hotwords == len(detected_callback), \
            "Error: hotwords in your models (%d) do not match the number of " \
            "callbacks (%d)" % (self.num_hotwords, len(detected_callback))

        logger.debug("detecting...")

        state = "PASSIVE"
        while self._running is True:
            if interrupt_check():
                logger.debug("detect voice break")
                break
            data = self.ring_buffer.get()
            if len(data) == 0:
                time.sleep(sleep_time)
                continue

            status = self.detector.RunDetection(data)
            if status == -1:
                logger.warning("Error initializing streams or reading audio data")

            #small state machine to handle recording of phrase after keyword
            if state == "PASSIVE":
                if status > 0: #key word found
                    self.recordedData = []
                    self.recordedData.append(data)
                    silentCount = 0
                    recordingCount = 0
                    message = "Keyword " + str(status) + " detected at time: "
                    message += time.strftime("%Y-%m-%d %H:%M:%S",
                                         time.localtime(time.time()))
                    logger.info(message)
                    callback = detected_callback[status-1]
                    if callback is not None:
                        callback()

                    if audio_recorder_callback is not None:
                        state = "ACTIVE"
                    continue

            elif state == "ACTIVE":
                stopRecording = False
                if recordingCount > recording_timeout:
                    stopRecording = True
                elif status == -2: #silence found
                    if silentCount > silent_count_threshold:
                        stopRecording = True
                    else:
                        silentCount = silentCount + 1
                elif status == 0: #voice found
                    silentCount = 0

                if stopRecording == True:
                    fname = self.saveMessage()
                    audio_recorder_callback(fname)
                    state = "PASSIVE"
                    continue

                recordingCount = recordingCount + 1
                self.recordedData.append(data)

        logger.debug("finished.")

    def saveMessage(self):
        filename = 'output' + str(int(time.time())) + '.wav'
        data = b''.join(self.recordedData)

        #use wave to save data
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(
            self.audio.get_format_from_width(
                self.detector.BitsPerSample() / 8)))
        wf.setframerate(self.detector.SampleRate())
        wf.writeframes(data)
        wf.close()
        logger.debug("finished saving: " + filename)
        return filename

    def terminate(self):
        self.stream_in.stop_stream()
        self.stream_in.close()
        self.audio.terminate()
        self._running = False
