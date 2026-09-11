"""
Script to find scenarios where a specific guess narrows the possible answers down to
just one. That one guess is preloaded in the WordleInOne.py game
"""

import random

OK_ANSWERS = set()
with open("WordleWordsList.txt", "r", encoding="utf-8") as f:
    for line in f:
        OK_ANSWERS.add( line.strip().upper() )

GUESSES = []
with open("WordleGuessesList.txt", "r", encoding="utf-8") as f:
    for line in f:
        GUESSES.append( line.strip().upper() )


def encode(color_nums: list[int]) -> int:
    """Encode the 5 numbers in 0..2 into one base 3 number"""
    return sum(color_nums[4-i] * 3**i for i in range(5))

def decode(color_hash: int) -> list[int]:
    ret = [-1] * 5
    for i in range(5):
        ret[4-i] = color_hash % 3
        color_hash //= 3
    return ret

def color(guess: str, answer: str) -> int:
    target_ct = {c : 0 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    guess_ct = {c : 0 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}

    result = [-1] * 5

    # Find green and grey
    for i in range(5):
        # Green
        if guess[i] == answer[i]:
            result[i] = 2
        # Grey
        elif guess[i] not in answer:
            result[i] = 0
            target_ct[answer[i]] += 1
        else:
            target_ct[answer[i]] += 1
            guess_ct[guess[i]] += 1

    for i in range(5):
        if result[i] != -1:
            continue
        c = guess[i]
        if target_ct[c] >= guess_ct[c]:
            target_ct[c] -= 1
            result[i] = 1
        else:
            result[i] = 0
    
    return encode(result)


# --- Solver function -------------------------

MAX_N = 243 #encode([2, 2, 2, 2, 2]) + 1

def generate_wordle_in_one() -> tuple[str, str]:

    while True:
        guess = random.choice(GUESSES)

        buckets = [[] for _ in range(MAX_N)]

        for answer in GUESSES:
            color_hash = color(guess, answer)
            if len(buckets[color_hash]) <= 1:
                buckets[color_hash].append(answer)

        ret = []
        for i in range(MAX_N - 1): # exclude the all GREEN guess
            if len(buckets[i]) == 1 and buckets[i][0] in OK_ANSWERS:
                ret.append(buckets[i][0])
        if ret:
            return (guess, random.choice(ret))
