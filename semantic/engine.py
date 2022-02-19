import os
import time

from crawler import scrapper
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


def load_tf_idf_separately(path):
    index_map = {}

    with open(path) as file:
        for line in file.readlines():
            values = line.strip().split(' ')
            if values[0].split('.')[0] not in index_map.keys():
                index_map[values[0].split('.')[0]] = {}
            index_map[values[0].split('.')[0]][values[1]] = float(values[2])
    print('Loaded context')
    # pretty(index_map)
    return index_map


def find(to_find, index_dict):
    matched = set()

    tokens = tokenizer.tokenize(to_find)
    lemmas = tokenizer.lemmatize(tokens).keys()

    for lemma in lemmas:
        matched.update(index_dict.get(lemma, []))

    return matched


BOOLEAN_TERMS = ['&', '|']


def parse(expression, index_dict, tf_idf_index):
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


def create_query_vector(query, lemmas_intersection, idf_index):
    query_vector = dict.fromkeys(lemmas_intersection, 0.0)

    query_idf = {lemma: float(idf_index[lemma][0]) for lemma in lemmas_intersection}

    query_tf = dict.fromkeys(lemmas_intersection, 0)
    index.termfreq_for_lemmas(query, query_tf)

    for key in query_vector.keys():
        query_vector[key] = float(query_tf[key]) * float(query_idf[key])
    return query_vector


def create_pages_vectors(lemmas_intersection, tf_sep_index, idf_index, pages):
    pages_vectors = dict.fromkeys(pages, 0)

    pages_idf = {lemma: float(idf_index[lemma][0]) for lemma in lemmas_intersection}

    for page in pages_vectors.keys():
        page_tf = tf_sep_index[page]
        pages_vectors[page] = {lemma: float(page_tf[lemma]) * pages_idf[lemma] for lemma in lemmas_intersection}
    return pages_vectors


def dotProduct(doc1, doc2):
    lemmas = doc1.keys()
    if len(doc1) != len(doc2):
        return 0
    if len(doc1.keys()) > 1:
        return sum([x * y for x, y in zip((doc1[lemma] for lemma in lemmas), (doc2[lemma] for lemma in lemmas))])
    else:
        return list(doc1.values())[0] * list(doc2.values())[0]


def parse_vector(query, index_dict, tf_sep_index, idf_index):
    query_lemmas = index.lemmatize(index.tokenize(query))
    lemmas_intersection = index.get_unique_lemmas().intersection(query_lemmas)

    query_vector = create_query_vector(query, lemmas_intersection, idf_index)

    query_splitted = query.split()

    pages = find(query_splitted[0], index_dict)
    for i in range(len(query_splitted) - 1):
        found = find(query_splitted[i + 1], index_dict)
        pages.update(found)

    page_vectors = create_pages_vectors(lemmas_intersection, tf_sep_index, idf_index, pages)

    results = [[dotProduct(page_vectors[result], query_vector), result] for result in pages]
    results.sort(key=lambda x: x[0])
    results = [x[1] for x in results]
    return results



if __name__ == '__main__':
    start_time = time.time()
    index_dict = load_index(index.INVERTED_INDEX_PATH)
    idf_index = load_index(index.TF_IDF_LEMMA_INDEX_PATH)
    tf_sep_index = load_tf_idf_separately(index.TF_IDF_LEMMA_INDEX_SEPARATED_PATH)
    print("Context loading finished in %s seconds" % (time.time() - start_time))
    print("Print request to find: ", end="")

    to_find = input()
    while to_find != '@exit':
        start_time = time.time()
        # match_file = parse(to_find, index_dict, tf_idf_index)
        match_file = parse_vector(to_find, index_dict, tf_sep_index, idf_index)
        print("Request took %s seconds" % (time.time() - start_time))
        if len(match_file):
            print(match_file)
        else:
            print("Couldn't find anything")

        print("Print request to find: ", end="")
        to_find = input()
