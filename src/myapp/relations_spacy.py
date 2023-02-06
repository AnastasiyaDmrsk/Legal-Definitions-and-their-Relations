# identifying semantic relations using spaCy and semantic role labeling
# inspired by spacy documentation: https://spacy.io/usage/spacy-101

import spacy


def find_semantic_relations(annotations):
    nlp = spacy.load("en_core_web_sm")
    for key, value in annotations.items():
        sentence = key + " " + value
        doc = nlp(sentence)
        print(sentence)
        for token in doc:
            print(token.text, token.pos_)
