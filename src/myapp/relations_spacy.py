# identifying semantic relations using spaCy and semantic role labeling
# inspired by spacy documentation: https://spacy.io/usage/spacy-101

import spacy


def find_semantic_relations(relations):
    # in relations key is the left side of the relation aka hyponym and values are the right side of the relation
    # TODO: mehrere mögliche Relationen abspeichern --> z.B mit , getrennt
    # relations = {}
    all_relations = []
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
                if token.i > 0 and doc[token.i-1].pos_ == "ADJ":
                    relation = doc[token.i-1].text + " " + relation
                if token.nbor().pos_ == "ADP":
                    while len(doc) - 1 > token.idx and token.nbor().pos_ != "NOUN":
                        relation = relation + " " + token.nbor().text
                        token = token.nbor()
                    relation = relation + " " + token.nbor().text
                relation_list.append(relation)
                if token.nbor().pos_ == "CCONJ":
                    token = token.nbor()
                    continue
                # relations[key] = relation_list
                # print(key + " is a hyponym of " + relations[key])
                for rel in relation_list:
                    print(key + " is a hyponym of " + rel)
                    all_relations.append(key + " is a hyponym of " + rel)
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
        # print(relationships_str)
        relations.append(relationships_str.__str__())
        print(relations)
    return relations
