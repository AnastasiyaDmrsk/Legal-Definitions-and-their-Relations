import re
from collections import Counter

annotations = {}
counter_set = {}  # counts the frequency of each definition
sentences_set = {}
articles_set = {}
articles_set_and_frequency = {}


def find_definitions(soup):
    defin = []
    global annotations
    annotations = {}
    # extract only the article which contains definitions
    start_class = soup.find("p", string="Definitions")
    end_class = soup.find("p", string=re.compile("Article"))
    # extract the definitions and their explanations
    for element in start_class.next_siblings:
        if element == end_class:
            break
        if element.text.__contains__("’") & element.text.__contains__("mean"):
            full_def = element.text.replace("\n\n", "\n")
            first_index = full_def.find("‘")
            second_index = full_def.find("’", first_index + 1)
            # check for apostrophe inside the definition
            while len(full_def) > second_index + 1 and full_def[second_index + 1].isalpha():
                second_index = full_def.find("’", second_index + 1)
            if first_index != -1 and second_index != -1:
                only_def = full_def[first_index + 1:second_index]
                # only_def = full_def.split("’")[0].strip()
                # match = re.search("[a-zA-Z]", only_def)
                # if match:
                # TODO: falls mehrere Beschreibungen vorhanden sind, sollen die abgespeichert werden
                # TODO: falls mehrere Definitionen eine Beschreibung haben wie sollen die dann abgespeichert werden
                if len(full_def.split(only_def + '’ ')) > 1:
                    only_expl = full_def.split(only_def + '’ ')[1].strip()
                    annotations[only_def] = only_expl
                    # print("Definition: " + only_def + " and Explanation: " + only_expl)
                    defin.append(full_def.replace("\n\n", "\n"))
                # else:
                # print("I can't find the definition: " + full_def)
    definitions = "".join(defin)
    return definitions


def check_definition_part_of_another_definition(definition):
    part_def = []
    for key in annotations.keys():
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
    for key, value in annotations.items():
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
                article_counter = 0
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
