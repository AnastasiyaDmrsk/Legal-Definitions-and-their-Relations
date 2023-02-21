import re
import nltk
from collections import Counter
from nltk.corpus import wordnet as wn
import spacy

annotations = {}  # only 1:1 relations --> better for pure printing
counter_set = {}  # counts the frequency of each definition
sentences_set = {}
articles_set = {}
definitions = {}  # definitions n:m
articles_set_and_frequency = {}
definitions_list = list(tuple())  # in this list each element is a tuple (definition, explanation)
nltk.download('wordnet')


def find_definitions(soup):
    global annotations
    annotations = {}
    global definitions_list
    definitions_list = list(tuple())
    # extract only the article which contains definitions
    start_class = soup.find("p", string="Definitions")
    end_class = soup.find("p", string=re.compile("Article"))
    # extract the definitions and their explanations
    for element in start_class.next_siblings:
        if element == end_class:
            break
        if re.match(r"^Article \d+$", element.text.strip()):
            break
        process_definitions(element.text)
    return definitions_list


def check_definition_part_of_another_definition(definition):
    part_def = []
    for (key, value) in definitions_list:
        if key.__contains__(definition) and key != definition:
            part_def.append(key)
    return part_def


def check_multiple_explanations(definition):
    if annotations[definition].__contains__("; or"):
        return True
    return False


def format_document(s):
    global counter_set
    counter_set = {}
    global sentences_set
    sentences_set = {}
    # leaving only enacting terms
    start_class = s.find("p", string="HAVE ADOPTED THIS REGULATION:")
    end_class = s.find("div", {"class": "final"})
    global definitions_list
    for (key, value) in definitions_list:
        counter = 0
        all_sentences = ""
        article = ""
        articles_set[key] = set()
        articles_set_and_frequency[key] = list()
        d = check_definition_part_of_another_definition(key)
        for element in start_class.next_siblings:
            if element == end_class:
                break
            pattern = r"^Article \d+$"
            if re.match(pattern, element.text):
                article = element.text
            if key in element.text:
                # check if exactly this definition is mentioned or another one
                if d.__len__() != 0:
                    for k in d:
                        if check_two_definitions_in_text(key, k, element.text):
                            break
                counter += 1
                new_text = element.text.replace("\n\n", "\n").strip()
                all_sentences = all_sentences + "\n" + "Sentence " + str(counter) + ": " + new_text
                articles_set[key].add(article)
                articles_set_and_frequency[key].append(article)

        sentences_set[key] = all_sentences
        counter_set[key] = counter


def most_frequent_definitions():
    def_list = []
    sorted_def = sorted(counter_set, key=counter_set.get, reverse=True)
    if len(sorted_def) >= 5:
        top_five = sorted_def[:5]
        for element in top_five:
            def_list.append(element + ": " + str(counter_set[element]) + " hits in " +
                            len(articles_set[element]).__str__() + " articles")
    return def_list


def get_article_number(article):
    return int(article.split()[1])


def get_annotations():
    return annotations


def get_sentences():
    return sentences_set


def get_counter():
    return counter_set


def get_articles(key):
    articles = ", ".join(sorted(articles_set[key], key=get_article_number))
    return articles


def calculate_the_frequency(key):
    counter = Counter(articles_set_and_frequency[key])
    repeated_elements = [(element, count) for element, count in counter.items()]
    articles = "Definition " + key + " can be found in: "
    for (element, count) in repeated_elements:
        articles = articles + element + " with " + str(count) + " number of hits; "
    return articles


# return True if only the longest definition (definition2) occurs, but the shortest does not
def check_two_definitions_in_text(definition1, definition2, text):
    if not text.__contains__(definition2):
        return False
    strings = text.split(definition2)
    new_string = "".join(strings)
    if new_string.__contains__(definition1):
        return False
    return True


# return True if only the longest definitions occur in the text, but the shortest does not
def check_more_definitions_in_text(definition1, text):
    definition_set = check_definition_part_of_another_definition(definition1)
    for s in definition_set:
        if check_two_definitions_in_text(definition1, s, text):
            return True
    return False


def is_synonym(verb):
    if verb == "mean" or verb == "include" or verb == "be":
        return True
    # since most of the regulations have mean as a verb or include, we compare the verb to the synonyms of them
    mean_synsets = wn.synsets('mean', pos='v')
    mean_synonyms = set(lemma.name() for synset in mean_synsets for lemma in synset.lemmas())
    include_synsets = wn.synsets('include', pos='v')
    include_synonyms = set(lemma.name() for synset in include_synsets for lemma in synset.lemmas())
    be_synsets = wn.synsets('be', pos='v')
    be_synonyms = set(lemma.name() for synset in be_synsets for lemma in synset.lemmas())
    if verb in mean_synonyms or verb in include_synonyms or verb in be_synonyms:
        return True
    return False


def process_definitions(text):
    if text.__contains__("’"):
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text.split(";")[0])  # this way only the most important part of the definition will be examined
        definition_set = set()
        explanation_set = set()
        # search for the first verb after the definition
        first_verb = None
        for token in doc:
            if token.dep_ == "ROOT" and (token.pos_ == "VERB" or token.pos_ == "AUX"):
                first_verb = token
                break
        if first_verb is not None and is_synonym(first_verb.lemma_):
            definition = text[:first_verb.idx].strip()
            explanation = text[first_verb.idx:].strip()
            d = [s for s in definition.split("\n") if s != ""]
            e = [s for s in explanation.split("\n") if s != ""]
            save_in_annotations("".join(d), "".join(e))
            for element in d:
                if element.__contains__("‘"):
                    if element.__contains__(" and ‘") or element.__contains__(" or ‘") or element.__contains__(", ‘"):
                        definition_set = split_multiples(element)
                    else:
                        definition_set.add(element)
            for element_e in e:
                if element_e != "" and element_e[0] != "(":
                    explanation_set.add(element_e)
            global definitions
            save_in_list(definition_set, explanation_set)
            d_set = tuple(definition_set)
            definitions[d_set] = explanation_set


def split_multiples(text):
    result = set()
    if text.__contains__(",") and text.__contains__(" and "):
        elements = text.split(", ")
        for e in elements:
            if not e.__contains__(" and "):
                result.add(e)
            else:
                el = e.split(" and ")
                for e1 in el:
                    result.add(e1)
    elif text.__contains__(",") and text.__contains__(" or "):
        elements = text.split(",")
        for e in elements:
            if e.__contains__(" or "):
                el = e.split(" or ")
                for e1 in el:
                    result.add(e1)
            else:
                result.add(e)
    elif text.__contains__(" or "):
        result = text.split(" or ")
    elif text.__contains__(" and "):
        result = text.split(" and ")
    return result


def save_in_list(set1, set2):
    for s in set1:
        for s2 in set2:
            global definitions_list
            start = s.find("‘")
            end = s.rfind("’")
            definitions_list.append((s[start + 1:end], s2))


def save_in_annotations(definition, explanation):
    global annotations
    annotations[definition] = explanation
