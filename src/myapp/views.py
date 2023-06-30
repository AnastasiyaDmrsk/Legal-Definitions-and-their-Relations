import re
import unicodedata
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import requests
from bs4 import BeautifulSoup
from django.http import FileResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from myapp.definitions import find_definitions, get_annotations, \
    check_more_definitions_in_text, any_definition_in_text, get_dictionary
from myapp.relations_spacy import noun_relations, build_tree, get_hyponymy, construct_ontology_graph, \
    construct_default_graph, get_meronymy, get_synonymy
from .forms import FormCELEX, FormDefinition

site = ""
celex = ""
reg_title = ""
definitions = list(tuple())
relations = ""
annotations = {}
regulation_with_annotations = ""
done_date = ""
regulation_body = ""
current_def = ""

counter_set = {}  # counts the frequency of each definition
sentences_set = {}
articles_set = {}
articles_set_and_frequency = {}


def index(request):
    if request.method == 'POST':
        form = FormCELEX(request.POST)

        if form.is_valid():
            global celex
            celex = form.cleaned_data['number']
            global site
            site = load_document(celex)
            return HttpResponseRedirect('result/')
    else:
        form = FormCELEX()
    return render(request, 'myapp/index.html', {'form': form})


def original_document(request):
    global site
    return HttpResponseRedirect(site)


def load_document(celex):
    # https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679&from=EN
    new_url = 'https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:' + celex + '&from=EN'
    return new_url


def result(request):
    extract_text(site)
    if len(most_frequent_definitions()) >= 5:
        context_dict = {'site': site, 'celex': celex, 'definitions': definitions,
                        'num_def': len(annotations.keys()),
                        'title': reg_title, 'date': done_date, 'frequent1': most_frequent_definitions()[0],
                        'frequent2': most_frequent_definitions()[1], 'frequent3': most_frequent_definitions()[2],
                        'frequent4': most_frequent_definitions()[3], 'frequent5': most_frequent_definitions()[4]}
    elif len(most_frequent_definitions()) == 4:
        context_dict = {'site': site, 'celex': celex, 'definitions': definitions,
                        'num_def': len(annotations.keys()),
                        'title': reg_title, 'date': done_date, 'frequent1': most_frequent_definitions()[0],
                        'frequent2': most_frequent_definitions()[1], 'frequent3': most_frequent_definitions()[2],
                        'frequent4': most_frequent_definitions()[3]}
    elif len(most_frequent_definitions()) == 3:
        context_dict = {'site': site, 'celex': celex, 'definitions': definitions,
                        'num_def': len(annotations.keys()),
                        'title': reg_title, 'date': done_date, 'frequent1': most_frequent_definitions()[0],
                        'frequent2': most_frequent_definitions()[1], 'frequent3': most_frequent_definitions()[2]}
    else:
        context_dict = {'site': site, 'celex': celex, 'definitions': definitions,
                        'num_def': len(annotations.keys()),
                        'title': reg_title, 'date': done_date}
    return render(request, 'myapp/result.html', context_dict)


# for testing purposes of assignment of annotations
def annotations_page(request):
    context_dict = {'body': regulation_body}
    return render(request, 'myapp/annotations.html', context_dict)


# for relation graph
def graph(request):
    defin = get_dictionary()
    image_path = 'myapp/static/myapp/graph.png'

    # if user enters an existing legal definition then construct a graph
    if request.method == 'POST':
        form = FormDefinition(request.POST)

        if form.is_valid():
            global current_def
            current_def = form.cleaned_data['definition']

            # construct a graph depending on the relation
            relation = form.cleaned_data['relation']
            if relation == 'meronymy':
                graph = construct_ontology_graph(get_meronymy(), current_def)
            elif relation == 'synonymy':
                graph = construct_ontology_graph(get_synonymy(), current_def)
            else:
                graph = construct_ontology_graph(get_hyponymy(), current_def)

            plt.figure(figsize=(8, 8))
            pos = nx.circular_layout(graph)

            colors = []
            for node in list(graph.nodes):
                if node == current_def:
                    colors.append('red')
                elif node in defin:
                    colors.append('pink')
                else:
                    colors.append('lightblue')

            sizes = [2000 if node_name == current_def else 1500 for node_name in list(graph.nodes)]
            nx.draw(graph, pos, with_labels=True, node_color=colors, node_size=sizes, font_size=9,
                    font_weight='bold', edge_color='gray', arrows=True)
            plt.margins(0.25, tight=False)
            plt.title('Ontology Graph')

            description = 'Selected definition: ' + current_def.upper() + "." + " Number of hits: " + \
                          str(len(sentences_set[current_def])) + ". " + calculate_the_frequency(current_def)
            plt.figtext(0.5, 0, description, wrap=True, horizontalalignment='center', fontsize=11)

            plt.savefig(image_path)
            return render(request, 'myapp/graph.html',
                          {'form': form, 'definitions': defin, 'image_path': 'myapp/graph.png'})
    else:
        # if the user enters no definition then create a default graph
        form = FormDefinition()
        g = construct_default_graph()
        plt.figure(figsize=(8, 8))
        pos = nx.circular_layout(g)
        nx.draw(g, pos, with_labels=True, node_color='gray', node_size=2500, font_size=11,
                font_weight='bold', edge_color='gray', arrows=True)
        plt.savefig(image_path)
    return render(request, 'myapp/graph.html', {'form': form, 'definitions': defin, 'image_path': 'myapp/graph.png'})


def extract_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    global reg_title
    reg_title = find_title(soup)
    global definitions
    definitions = find_definitions(soup)
    global done_date
    done_date = soup.find(string=re.compile("Done at"))
    global annotations
    annotations = get_annotations()
    add_annotations_to_the_regulation(soup)
    global regulation_body
    regulation_body = soup.body
    global regulation_with_annotations
    # adding some styling to the annotations
    regulation_with_annotations = '<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <title>Annotations' \
                                  '</title><style>[data-tooltip] {position: relative;}' \
                                  '[data-tooltip]::after {content:' \
                                  'attr(data-tooltip);position: absolute; width: 400px; left: 0; top: 0; background: ' \
                                  '#3989c9; color: #fff; padding: 0.5em; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); ' \
                                  'pointer-events: none; opacity: 0; transition: 1s; } [data-tooltip]:hover::after ' \
                                  '{opacity: 1; top: 2em; z-index: 99999; right: max(20px, calc(100% - 220px));} ' \
                                  '</style></head>"' + str(regulation_body) + '</html>'
    global relations
    relations = "\n".join(noun_relations(definitions))
    # uncomment for evaluation purposes
    # compare_sentences()
    # compare_definitions_and_relations()


def add_annotations_to_the_regulation(soup):
    global sentences_set
    sentences_set.clear()
    global articles_set
    articles_set.clear()
    global articles_set_and_frequency
    articles_set_and_frequency.clear()
    article = ""
    # case if a regulation has div for each article
    if soup.find("div", id="001") is not None:
        for div in soup.find_all("div"):
            div.unwrap()
    for sentence in soup.find_all("p"):
        if check_if_article(sentence.text):
            article = sentence.text
        for (key, value) in definitions:
            if sentence.text.__contains__(key):
                text = sentence.text
                sentence.clear()
                if not check_more_definitions_in_text(key, sentence.text):
                    # sort by the starting index
                    defs = sorted(any_definition_in_text(text), key=lambda x: x[2])
                    start_index = 0
                    for (k, v, start, end) in defs:
                        sentence.append(text[start_index:start])
                        tag = create_new_tag(soup, text, k, v, start, end)
                        sentence.append(tag)
                        start_index = end
                        sent = text.replace("\n\n", "\n").strip()
                        sent = unicodedata.normalize("NFKD", sent)
                        if k not in sentences_set:
                            sentences_set[k] = set()
                        sentences_set[k].add(sent)
                        if k not in articles_set:
                            articles_set[k] = set()
                        articles_set[k].add(article)
                        if k not in articles_set_and_frequency:
                            articles_set_and_frequency[k] = list()
                        articles_set_and_frequency[k].append(article)
                    sentence.append(text[start_index:])


def check_if_article(text):
    if len(text) > 11 or not text.__contains__("Article"):
        return False
    new_text = text.replace("Article", "").strip()
    if new_text.isdigit():
        return True
    return False


# can be adjusted depending on the processed document
def find_title(s):
    start_class = s.find("p", string=re.compile("REGULATION"))
    if start_class is None:
        return ""
    end_class = s.find("p", string=re.compile("THE EUROPEAN PARLIAMENT AND THE COUNCIL"))
    title = str(start_class.text)
    for element in start_class.next_siblings:
        if element == end_class:
            break
        title = title + " " + element.text
    return title


def create_new_tag(soup, text, key, value, start, end):
    new_tag = soup.new_tag('span')
    new_tag["style"] = "background-color: yellow;"
    new_tag["data-tooltip"] = key + ' ' + value
    new_tag.string = text[start:end]
    return new_tag


def most_frequent_definitions():
    def_list = []
    sorted_def = sorted(sentences_set.items(), key=lambda x: len(x[1]), reverse=True)
    top_five_definitions = [definition[0] for definition in sorted_def[:5]]
    for d in top_five_definitions:
        def_list.append(d + ": " + str(len(sentences_set[d])) + " hits in " + len(articles_set[d]).__str__() +
                        " articles")
    return def_list


def calculate_the_frequency(key):
    counter = Counter(articles_set_and_frequency[key])
    repeated_elements = [(element, count) for element, count in counter.items()]
    articles = "Definition " + key + " can be found in: Article "
    for (element, count) in repeated_elements:
        num = re.findall(r'\d+', element)
        articles = articles + "".join(num) + "; "  # + " with " + str(count) + " number of hits "
    return articles.replace(" ; ", " ")


def cut_tag(tag):
    new_string = str(tag)
    start = new_string.find(">")
    end = new_string.rfind("<")
    return new_string[start + 1:end]


def get_sentences():
    return sentences_set


# create a txt. file to download with all definitions and their explanations
def download_definitions_file(request):
    with open("file.txt", "w") as file:
        for key, value in annotations.items():
            file.write(key + " " + value + "\n")
    response = FileResponse(open("file.txt", 'rb'))
    response['Content-Disposition'] = 'attachment; filename="file.txt"'
    return response


# create a txt. file to download with all sentences with definitions
def download_sentences(request):
    with open("sentences.txt", "w") as file:
        for key in sentences_set:
            file.write("Definition: " + key + "\n")
            file.write("Total number of text segments including definition: " + str(len(sentences_set[key])) + "\n\n")
            file.write(calculate_the_frequency(key) + "\n\n")
            for sent in sentences_set[key]:
                file.write("\t\t" + sent + "\n\n")
            file.write("\n\n")
    response = FileResponse(open("sentences.txt", 'rb'))
    response['Content-Disposition'] = 'attachment; filename="sentences.txt"'
    return response


# create an HMTL file to download with annotations
def download_annotations(request):
    with open("annotated_page.html", "w") as file:
        file.write(regulation_with_annotations)
    response = FileResponse(open("annotated_page.html", "rb"))
    response['Content-Disposition'] = 'attachment; filename="annotated_page.html"'
    return response


# create a text file to download with all semantic relations listed
def download_relations(request):
    with open("relations.txt", "w") as file:
        file.write(relations)
        file.write("\n\n")
        file.write("Hyponymy Tree: \n")
        hyponymy = get_hyponymy()
        keys = set(hyponymy.keys())
        values = set().union(*hyponymy.values())
        roots = keys.difference(values)
        for root in roots:
            file.write(build_tree(root))
    response = FileResponse(open("relations.txt", 'rb'))
    response['Content-Disposition'] = 'attachment; filename="relations.txt"'
    return response
