"""Day 1, step 8: token counts and speed from a streamed call."""

import json

import httpx

URL = "http://127.0.0.1:11434/v1/chat/completions"

body = {
    "model": "qwen2.5:7b",
    "messages": [
        {"role": "user", "content": "Write 500 words about how a reverse proxy works."}
    ],
    "stream": True,
    "stream_options": {"include_usage": True},
    "temperature": 0,
}

with httpx.stream(
    "POST", URL, json=body, timeout=httpx.Timeout(60.0, connect=5.0)
) as r:
    r.raise_for_status()
    for line in r.iter_lines():
        if not line.startswith("data: "):
            continue
        data = line.removeprefix("data: ")
        if data == "[DONE]":
            break
        chunk = json.loads(data)
        if not chunk["choices"]:  # the extra chunk at the end: no text, only counts
            print("usage:", chunk["usage"])
            print("timings:", chunk.get("timings"))
            print(
                "tokens a second:", round(chunk["timings"]["predicted_per_second"], 1)
            )
