import time

from semantic import tokenizer, index


def pretty(d, indent=0):
    for key, value in d.items():
        print('\t' * indent + str(key))
        if isinstance(value, dict):
            pretty(value, indent + 1)
        else:
            print('\t' * (indent + 1) + str(value))


def load_idf(path):
    index_map = {}

    with open(path) as file:
        for line in file.readlines():
            values = line.strip().split(' ')
            index_map[values[0]] = values[1:]
    print('Loaded context')
    pretty(index_map)
    return index_map


def load_index(path):
    index_map = {}

    with open(path) as file:
        for line in file.readlines():
            values = line.strip().split(' ')
            index_map[values[0]] = values[1:]
    print('Loaded context')
    pretty(index_map)
    return index_map


def find(to_find, index_dict):
    matched = set()

    tokens = tokenizer.tokenize(to_find)
    lemmas = tokenizer.lemmatize(tokens).keys()

    for lemma in lemmas:
        matched.update(index_dict.get(lemma, []))

    return matched


BOOLEAN_TERMS = ['&', '|']


def parse(expression, index_dict, idf_index):
    expression = expression.split(" ")

    bools = []
    answer = set()
    for word in expression:
        bools.append(word in BOOLEAN_TERMS)

    answer = find(expression[0], index_dict)
    for i, bool in enumerate(bools):
        if bool:
            if expression[i] in BOOLEAN_TERMS:
                found = find(expression[i + 1], index_dict)
                if expression[i] == '&':
                    answer.intersection(found)
                if expression[i] == '|':
                    answer.update(found)
    return answer


if __name__ == '__main__':
    start_time = time.time()
    index_dict = load_index(index.INVERTED_INDEX_PATH)
    idf_index = load_index(index.TF_IDF_LEMMA_INDEX_PATH)
    print("Context loading finished in %s seconds" % (time.time() - start_time))
    print("Print word to find: ", end="")

    to_find = input()
    while to_find != '@exit':
        start_time = time.time()
        match_file = parse(to_find, index_dict, idf_index)
        print("Request took %s seconds" % (time.time() - start_time))
        if len(match_file):
            print(match_file)
        else:
            print("Couldn't find anything")

        print("Print word to find: ", end="")
        to_find = input()
