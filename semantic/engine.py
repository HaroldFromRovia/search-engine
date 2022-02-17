from semantic import tokenizer
from semantic.index import Index, index


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


def load_index(path):
    index_map = {}

    with open(path) as file:
        for line in file.readlines():
            values = line.strip().split(' ')
            index_map[values[0]] = values[1:]
    print('Loaded context')
    pretty(index_map)
    return Index((key, value) for key, value in index_map.items())


def find(to_find, index_dict):
    matched = set()

    tokens = tokenizer.tokenize(to_find)
    lemmas = tokenizer.lemmatize(tokens).keys()

    for lemma in lemmas:
        matched.update(index_dict.get(lemma, []))

    return matched


if __name__ == '__main__':

    index_dict = load_index(index.INVERTED_INDEX_PATH)
    print("Print word to find: ", end="")

    to_find = input()
    while to_find != '@exit':
        match_file = find(to_find, index_dict)
        if len(match_file):
            print(match_file)
        else:
            print("Couldn't find anything")

        print("Print word to find: ", end="")
        to_find = input()
