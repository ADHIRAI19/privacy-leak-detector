from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
import json
from openai import OpenAI
from privacy_leak_detector.env import PrivacyLeakEnv, Action
from privacy_leak_detector.graders import Detection

app = FastAPI(title="Privacy Leak Detector OpenEnv")

class ResetRequest(BaseModel):
    task_id: int = 0

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"

task_names = ["Easy", "Medium", "Hard"]

env = PrivacyLeakEnv()
current_obs = None

def format_prompt(task_id):
    task = task_names[task_id]
    return f"""Privacy Leak Detection Task {task_id} ({task}): Analyze for privacy leaks.

Return JSON only:
{{
  "analysis": "your analysis",
  "risk_level": "low|medium|high|critical",
  "detections": [{{"type": "email", "value": "example@domain.com", "confidence": 0.95}}]
}}"""

@app.post("/openenv/reset")
async def reset(request: ResetRequest):
    global current_obs, env
    env = PrivacyLeakEnv()
    current_obs = env.reset(request.task_id)
    return {"status": "reset done", "task_id": request.task_id}

@app.post("/openenv/validate")
async def validate():
    return {"status": "ok", "endpoints": ["/openenv/reset", "/openenv/validate", "/step"]}

@app.post("/step")
async def step():
    global current_obs

    prompt = format_prompt(current_obs.task_id)

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    try:
        content = resp.choices[0].message.content
        action_dict = json.loads(content)
        action = Action(**action_dict)
    except:
        action = Action(analysis="AI response parse error", risk_level="low", detections=[])

    obs, reward, done, info = env.step(action)
    current_obs = obs

    return {
        "observation": obs.dict(),
        "reward": reward,
        "done": done,
        "info": info
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
