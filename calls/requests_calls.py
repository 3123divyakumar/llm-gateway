"""Day 1, step 6: the same two calls as curl.exe, from Python with requests."""

import json

import requests

URL = "http://127.0.0.1:11434/v1/chat/completions"
TIMEOUT = (5, 60)  # 5 s to connect, 60 s of silence between two pieces


def ask(question: str) -> str:
    body = {
        "model": "qwen2.5:7b",
        "messages": [{"role": "user", "content": question}],
        "stream": False,
        "temperature": 0,
    }
    r = requests.post(URL, json=body, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def ask_streamed(question: str) -> None:
    body = {
        "model": "qwen2.5:7b",
        "messages": [{"role": "user", "content": question}],
        "stream": True,
        "temperature": 0,
    }
    with requests.post(URL, json=body, timeout=TIMEOUT, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line.startswith("data: "):
                continue  # the blank lines between events
            data = line.removeprefix("data: ")
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            print(chunk["choices"][0]["delta"].get("content", ""), end="", flush=True)
    print()


if __name__ == "__main__":
    print(ask("What is a reverse proxy? One sentence."))
    print("---")
    ask_streamed("Explain a reverse proxy in 3 sentences.")
