#!/usr/bin/env python
import os
import json
from typing import Dict
from openai import OpenAI
from privacy_leak_detector.env import PrivacyLeakEnv, Observation, Action
from privacy_leak_detector.graders import Detection

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

print("[START] PrivacyLeakDetector baseline")

task_names = ["Easy", "Medium", "Hard"]

def format_prompt(obs):
    return f"""Task {obs.task_id} ({task_names[obs.task_id]}): {obs.text}

Score: {obs.current_score:.2f}

JSON response:
{{
  "analysis": "Risk analysis...",
  "risk_level": "medium",
  "detections": [{{"type": "keyword", "value": "password", "confidence": 0.95}}]
}}"""

def run_episode(task_id):
    env = PrivacyLeakEnv()
    obs = env.reset(task_id)
    print(f"[STEP 0] Task {task_id}")
    
    prompt = format_prompt(obs)
    resp = client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": prompt}])
    
    try:
        action = Action(**json.loads(resp.choices[0].message.content))
    except:
        action = Action(analysis="Test", risk_level="low", detections=[Detection(type="test", value="test", confidence=0.5)])
    
    obs, reward, done, info = env.step(action)
    print(f"[END] Score: {info['final_score']:.3f}")
    return info['final_score']

for t in range(3):
    score = run_episode(t)
    print(f"Task {t}: {score}")

print("[COMPLETE]")

