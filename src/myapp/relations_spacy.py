# identifying semantic relations using spaCy and semantic role labeling
# inspired by spacy documentation: https://spacy.io/usage/spacy-101

import spacy
from myapp.definitions import get_dictionary
from collections import defaultdict

hyponymy = {}
all_relations = list()


def noun_relations(definitions):
    global hyponymy
    hyponymy.clear()
    global all_relations
    all_relations = list()
    nlp = spacy.load("en_core_web_sm")
    for (key, value) in definitions:
        sentence = value.replace("- ", "-")
        doc = nlp(sentence)
        for noun in doc.noun_chunks:
            if single_relation(doc[noun.end:]):
                save_to_hyponymy(noun, key)
                break
            save_to_hyponymy(noun, key)
    find_synonyms()
    return sorted(set(all_relations))


def find_synonyms():
    synonym_keys = defaultdict(list)
    for k, v in get_dictionary().items():
        synonym_keys[v].append(k)
    result_synonyms = [tuple(keys) for keys in synonym_keys.values() if len(keys) > 1]
    global all_relations
    for synonyms in result_synonyms:
        s = ""
        for synonym in synonyms:
            s += synonym + ", "
        all_relations.append(s[:-2] + " are synonyms")


def save_to_hyponymy(noun, key):
    hyponym_noun = ""
    for noun_token in noun:
        if noun_token.pos_ != "PRON" and noun_token.pos_ != "DET":
            hyponym_noun += noun_token.text + " "
    if hyponym_noun != "":
        all_relations.append(key + " is a hyponym of " + hyponym_noun.strip())
    hypernym = hyponym_noun.strip()
    if hypernym not in hyponymy and hypernym != "":
        hyponymy[hypernym] = set()
    if hypernym != "":
        hyponymy[hypernym].add(key)


def single_relation(doc):
    # check for , or and
    if doc[0].text == ',':
        return False
    if doc[0].text == "or" or doc[0].text == "and":
        return False
    else:
        return True


def get_hyponymy():
    return hyponymy


def build_tree(node, depth=0):
    result = '| ' * depth + node + '\n'
    if node not in hyponymy:
        return result
    for child in hyponymy[node]:
        result += build_tree(child, depth + 1)
    return result
