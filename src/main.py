import sys
from typing import Generator

from transformers import AutoTokenizer, pipeline, Pipeline
import torch

def get_model():
    # return "PY007/TinyLlama-1.1B-Chat-v0.1"
    return "PY007/TinyLlama-1.1B-Chat-v0.3"


def get_process(model):
    _ = AutoTokenizer.from_pretrained(model)

    process = pipeline(
        "text-generation",
        model=model,
        torch_dtype=torch.float16,
        device_map="auto",
    )

    return process


def get_prompt_start():
    return "Human:"

def get_prompt_end():
    return "Assistant:"


def get_prompt(prompt: str):
    prompt = prompt.strip(" #\n")
    return f"### {get_prompt_start()} {prompt} ### {get_prompt_end()} "


class Sequence:
    def __init__(self, /, prompt: str, answer: str) -> None:
        self.prompt = prompt
        self.answer = answer

    @staticmethod
    def from_generated_text(generated_text: str) -> "Sequence":
        generated_text = generated_text.replace(get_prompt_start(), "", 1)
        prompt, generated_text = generated_text.split(get_prompt_end(), 1)
        if get_prompt_start() in generated_text:
            answer, generated_text = generated_text.split(get_prompt_start(), 1)
        else:
            answer = generated_text

        return Sequence(
            prompt=prompt.strip(" #\n"),
            answer=answer.strip(" #\n"),
        )


def get_generation(formated_prompt: str, process: Pipeline, answers: int):
    sequences = process(
        formated_prompt,
        do_sample=True,
        top_k=50,
        top_p = 0.7,
        num_return_sequences=answers,
        repetition_penalty=1.1,
        max_new_tokens=500,
    )
    if not isinstance(sequences, (list, torch.Generator, Generator)):
        return []
    return list(map(lambda x: Sequence.from_generated_text(x["generated_text"]), sequences))


def main():
    prompt = sys.argv[1]
    formated_prompt = get_prompt(prompt)

    answers = 1
    if len(sys.argv) > 2:
        answers = int(sys.argv[2])

    model = get_model()
    process = get_process(model)

    for seq in get_generation(formated_prompt, process, answers):
        print(f"------------------------\n:: {seq.prompt} ::\n{seq.answer}\n")

main()
