from fastapi import FastAPI
import pydbus
import base64
from pydantic import BaseModel
from pathlib import Path
import hashlib

# Initialize FastAPI
app = FastAPI()

# Initialize pydbus
bus = pydbus.SystemBus()
signal = bus.get("org.asamk.Signal")

# Group ID
gID = [int(i) for i in base64.b64decode("base64 gID pls dont dox me")]

# Path for temporary audio files
tmpPath = Path("/tmp/radiowhisper_audio")

# Request body
# Yes we're doing this in the most inefficient way possible, whatever it's opus
# Plus w9yh is dead anyways
class ReqBody(BaseModel):
        transcript: str
        audio: str

@app.post("/")
async def root(req: ReqBody):
        tmpPath.mkdir(mode=0o770, exist_ok=True)
        filename = hashlib.sha1(req.transcript.encode()).hexdigest() + ".opus"
        file = tmpPath / filename
        with file.open("wb") as f:
                f.write(base64.b64decode(req.audio))
        signal.sendGroupMessage(req.transcript, [str(file.resolve())], gID)
        file.unlink()
        return {"status": "success"}
