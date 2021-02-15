from typing import List


def omissions(word: str) -> List[str]:
    words = []
    for i in range(len(word)):
        s = list(word)
        s.pop(i)
        words.append("".join(s))
    return words


def repetitions(word: str) -> List[str]:
    words = []
    for i in range(len(word)):
        words.append(word[0:i] + word[i] + word[i : len(word)])
    return words


def swaps(word: str) -> List[str]:
    words = []
    for i in range(len(word) - 1):
        s = list(word)
        s[i], s[i + 1] = s[i + 1], s[i]
        words.append("".join(s))
    return words
