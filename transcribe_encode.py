#!/home/noorquacker/.conda/envs/whisper/bin/python3
import socket
import numpy as np
import whisper
from ffmpeg import FFmpeg
import io
import requests
import base64


def upload(transcription, audio):
    enc_audio = base64.b64encode(audio).decode()
    body = {"transcript": transcription, "audio": enc_audio}
    requests.post("http://192.168.0.2:8000", json=body)


def encode(audio):
    ffmpeg = (
        FFmpeg()
        .option("y")
        .input("pipe:0", {"ar": 16000, "ac": 1}, f="f32le")
        .output("pipe:1", {"codec:a": "libopus", "ar": 48000}, f="opus")
    )
    try:
        opus = ffmpeg.execute(audio)
        print(
            f"Transcoded {len(audio)} bytes of f32le into {len(opus)} bytes of Opus data"
        )
        return opus
    except Exception as e:
        print(f"FFmpeg Exception {e}: {e.message} - {e.arguments}")
        return b""


def transcribe(model, audio):
    print("Transcribing...", end="")
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(
        model.device
    )
    options = whisper.DecodingOptions(language="English")
    result = whisper.decode(model, mel, options)
    return result.text


def looper(model, sock):
    # todo use bytesio
    buf = b""
    while True:
        try:
            data = sock.recv(1024)
            if len(buf) == 0:
                print("Receiving...", flush=True, end="")
            buf = buf + data
        except TimeoutError:
            if len(buf) > 0:
                arr = np.frombuffer(buf, dtype=np.float32)
                print(f"{arr.size} bytes!", flush=True)
                transcription = transcribe(model, whisper.pad_or_trim(arr))
                opus = encode(buf)
                upload(transcription, opus)
                print("Upload complete")
                buf = b""
            else:
                pass


def main():
    print("Loading model...")
    model = whisper.load_model("large-v3-turbo")
    print("Done! Binding socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("localhost", 2000))
    sock.settimeout(1)
    print("Listening on port 2000")
    looper(model, sock)


if __name__ == "__main__":
    main()
