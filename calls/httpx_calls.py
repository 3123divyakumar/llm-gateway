"""Day 1, step 7: the same calls with httpx, and the read timeout seen live.

Run:  uv run python calls/httpx_calls.py
"""

import json
import time

import httpx

URL = "http://127.0.0.1:11434/v1/chat/completions"
QUESTION = "Write 500 words about how a reverse proxy works."


def body(stream: bool) -> dict:
    return {
        "model": "qwen2.5:7b",
        "messages": [{"role": "user", "content": QUESTION}],
        "stream": stream,
        "temperature": 0,
    }


def not_streamed(timeout) -> None:
    start = time.perf_counter()
    try:
        r = httpx.post(URL, json=body(stream=False), timeout=timeout)
        r.raise_for_status()
        text = r.json()["choices"][0]["message"]["content"]
        print(
            f"  ok after {time.perf_counter() - start:.1f} s, {len(text.split())} words"
        )
    except httpx.ReadTimeout:
        print(f"  ReadTimeout after {time.perf_counter() - start:.1f} s")


def streamed() -> None:
    start = time.perf_counter()
    first = None
    pieces = 0
    with httpx.stream("POST", URL, json=body(stream=True)) as r:  # default timeout: 5 s
        r.raise_for_status()
        for line in r.iter_lines():
            if not line.startswith("data: "):
                continue
            data = line.removeprefix("data: ")
            if data == "[DONE]":
                break
            text = json.loads(data)["choices"][0]["delta"].get("content", "")
            if text and first is None:
                first = time.perf_counter() - start
            pieces += 1
    total = time.perf_counter() - start
    print(f"  first text at {first:.2f} s, {pieces} pieces, done at {total:.1f} s")


if __name__ == "__main__":
    print("1. not streamed, httpx's default timeout (5 s):")
    not_streamed(timeout=httpx.Timeout(5.0))
    print("2. not streamed, httpx.Timeout(60.0, connect=5.0):")
    not_streamed(timeout=httpx.Timeout(60.0, connect=5.0))
    print("3. streamed, default timeout:")
    streamed()
