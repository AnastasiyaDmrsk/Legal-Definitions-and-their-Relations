# identifying semantic relations using spaCy and semantic role labeling
# inspired by spacy documentation: https://spacy.io/usage/spacy-101

import spacy
from myapp.definitions import get_dictionary
from collections import defaultdict

hyponymy = {}
all_relations = list()


def find_semantic_relations(relations):
    # in relations key is the left side of the relation aka hyponym and values are the right side of the relation
    all_relations = set()
    nlp = spacy.load("en_core_web_sm")
    for (key, value) in relations:
        sentence = value
        doc = nlp(sentence)
        relation_list = []
        for token in doc:
            relation = ""
            if token.i == len(doc) - 1:
                break
            if token.pos_ == "NOUN":
                relation = relation + token.text
                if token.i > 0 and doc[token.i - 1].pos_ == "ADJ":
                    relation = doc[token.i - 1].text + " " + relation
                if token.nbor().pos_ == "ADP":
                    while len(doc) - 1 > token.i:
                        if token.nbor().pos_ != "NOUN":
                            relation = relation + " " + token.nbor().text
                            token = token.nbor()
                        else:
                            while len(doc) - 1 > token.i and token.nbor().pos_ == "NOUN":
                                relation = relation + " " + token.nbor().text
                                token = token.nbor()
                            break
                relation_list.append(relation)
                if token.nbor().pos_ == "CCONJ":
                    token = token.nbor()
                    continue
                for rel in relation_list:
                    all_relations.add(key + " is a hyponym of " + rel)
                break
    return all_relations


def extract_hypernyms(sentence):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(sentence)
    relationships = []
    print(sentence)
    for token in doc:
        print(token.text + " " + token.head.text + " " + token.dep_)
        if token.dep_ == "compound" or token.dep_ == "amod":
            hyponym = token.text
            hypernym = token.head.text
            relationships.append((hypernym, hyponym))
    return relationships


def extract_hypernyms_str(annotations):
    relations = []
    for key, value in annotations.items():
        sentence = "'" + key + "'" + " " + value
        relationships = extract_hypernyms(sentence)
        relationships_str = []
        for relationship in relationships:
            relationships_str.append(f"{relationship[1]} is a hyponym of {relationship[0]}")
        relations.append(relationships_str.__str__())
        print(relations)
    return relations


def noun_relations(definitions):
    global hyponymy
    hyponymy.clear()
    global all_relations
    all_relations = list()
    nlp = spacy.load("en_core_web_sm")
    for (key, value) in definitions:
        sentence = value
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
        if noun_token.pos_ == "NOUN" or noun_token.pos_ == "ADJ" or noun_token.pos_ == "CCONJ":
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
