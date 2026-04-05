from fastapi import FastAPI, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel
from privacy_leak_detector.env import PrivacyLeakEnv

app = FastAPI()

class AnalyzeRequest(BaseModel):
    text: str

@app.get("/")
async def root():
    return FileResponse("frontend.html")

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    env = PrivacyLeakEnv()
    return env.evaluate(request.text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
