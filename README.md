#  Privacy Leak Detector

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20HF%20Spaces-1f3e05)](https://huggingface.co/spaces/YOUR_USERNAME/privacy-leak-detector)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker)](https://hub.docker.com/)

## Environment Description & Motivation

**Privacy Leak Detector** is an OpenEnv-compliant RL environment simulating **real-world privacy risk assessment** in text data like emails, configs, logs.

**Why?** AI agents must learn to identify & classify privacy leaks accurately across difficulties, with continuous rewards.

### Tasks & Difficulties
| Task | Difficulty | Description | Expected Baseline Score |
|------|------------|-------------|-------------------------|
| 0 | Easy | Keyword detection (password, secret) | 0.8-0.9 |
| 1 | Medium | Structured (emails, phones, API keys) | 0.7-0.85 |
| 2 | Hard | Contextual ('my SSN', confidential) | 0.6-0.75 |

**Observation**: Text snippet, task_id, current detections/score.
**Action**: Analysis, risk_level, detections list.
**Reward**: Grader F1 + penalties (0.0-1.0).

## Setup

1. **Clone & Install**:
   ```
   git clone <repo>
   cd privacy-leak-detector
   pip install -r requirements.txt
   ```

2. **API Keys** (required for inference):
   Copy `.env.example` → `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```

3. **OpenEnv Validation**:
   ```
   openenv validate .
   ```

## Usage

### Baseline Inference
```
# Single task
python inference.py --task 0 --max-steps 10

# All tasks
python inference.py --all-tasks
```

Expected output: JSON trajectory with scores ~0.7+.

### Gradio Demo
```
gradio app.py
```
Test text snippets interactively.

### Docker
```
docker build -t privacy-leak-detector .
docker run -p 7860:7860 -e OPENAI_API_KEY=$OPENAI_API_KEY privacy-leak-detector
```

## HF Spaces Deployment
1. Push to HF repo.
2. Dockerfile auto-builds Gradio UI.

## Action/Observation Spaces
```python
Observation: {text: str, task_id: int, detections: List[Detection], score: float}
Action: {analysis: str, risk_level: str, detections: List[Detection]}
Detection: {type: str, value: str, confidence: float}
```

Pass `openenv validate` ✅ | Ready for RL training!

