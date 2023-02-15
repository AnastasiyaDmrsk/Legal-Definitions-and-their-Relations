import re

annotations = {}
counter_set = {}  # counts the frequency of each definition
sentences_set = {}


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
        d = check_definition_part_of_another_definition(key)
        for element in start_class.next_siblings:
            if element == end_class:
                break
            if key in element.text:
                # check if exactly this definition is mentioned or another one
                if d.__len__() == 0:
                    counter += 1
                    new_text = element.text.replace("\n\n", "\n").strip()
                    all_sentences = all_sentences + "\n" + "Sentence " + str(counter) + ": " + new_text
                else:
                    for k in d:
                        if not element.text.__contains__(k):
                            counter += 1
                            new_text = element.text.replace("\n\n", "\n").strip()
                            all_sentences = all_sentences + "\n" + "Sentence " + str(counter) + ": " + new_text
        sentences_set[key] = all_sentences
        counter_set[key] = counter


def most_frequent_definitions():
    def_list = []
    sorted_def = sorted(counter_set, key=counter_set.get, reverse=True)
    top_five = sorted_def[:5]
    for element in top_five:
        def_list.append(element + ": " + str(counter_set[element]) + " hits\n")
    return def_list


def get_annotations():
    return annotations


def get_sentences():
    return sentences_set


def get_counter():
    return counter_set
