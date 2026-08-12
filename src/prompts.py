def build_prompt(question: str, answer: str) -> str:
    return (
        f"Question: {question}\n"
        f"Answer: {answer}"
    )