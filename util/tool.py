import difflib
import re
from collections import defaultdict


def find_most_match_word(sentence, compare_word):
    words = re.findall(r'\w+', sentence)
    ratio_dct = defaultdict(float)
    for word in words:
        seq = difflib.SequenceMatcher(None, word, compare_word)
        ratio_dct[word] = seq.ratio()

    ret = sorted(ratio_dct, key=lambda key: ratio_dct[key], reverse=True)[0]
    return ret


if __name__ == '__main__':
    sentence = "We're invited to Lola's party."
    compare_word = 'invite'
    ans = find_most_match_word(sentence, compare_word)
