import os
from django.shortcuts import render
from .forms import FormCELEX
from django.http import HttpResponse, HttpResponseRedirect
import requests
import re
from bs4 import BeautifulSoup
from django.http import FileResponse
from myapp.relations_spacy import find_semantic_relations, extract_hypernyms_str
from myapp.definitions import find_definitions, get_annotations, check_definition_part_of_another_definition, \
    most_frequent_definitions, format_document, get_counter, get_sentences, calculate_the_frequency, \
    check_two_definitions_in_text

site = ""
celex = ""
reg_title = ""
definitions = ""
relations = ""
annotations = {}
regulation_with_annotations = ""
done_date = ""
regulation_body = ""


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
    context_dict = {'site': site, 'celex': celex, 'definitions': definitions, 'num_def': len(annotations.keys()),
                    'title': reg_title, 'date': done_date, 'frequent1': most_frequent_definitions()[0],
                    'frequent2': most_frequent_definitions()[1], 'frequent3': most_frequent_definitions()[2],
                    'frequent4': most_frequent_definitions()[3], 'frequent5': most_frequent_definitions()[4]}
    return render(request, 'myapp/result.html', context_dict)  # and the parameters for afterwards


def annotations_page(request):
    context_dict = {'body': regulation_body}
    return render(request, 'myapp/annotations.html', context_dict)


def extract_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    global reg_title
    reg_title = find_title(soup)
    global definitions
    definitions = find_definitions(soup)
    global done_date
    done_date = soup.find(string=re.compile("Done at"))
    # add annotations to the existing regulation
    global annotations
    annotations = get_annotations()
    for key, value in annotations.items():
        sentences = soup.find_all(string=re.compile(key))  # (string=lambda text: key in text)
        for sentence in sentences:
            d = check_definition_part_of_another_definition(key)
            new_tag = soup.new_tag('span')
            new_tag["data-tooltip"] = key + ' ' + value
            new_tag["style"] = "background-color: yellow;"
            new_tag.string = key
            if d.__len__() != 0:
                for k in d:
                    if check_two_definitions_in_text(key, k, sentence.text):
                        break
            parent = sentence.parent
            if parent.has_attr("data-tooltip") and not parent.get("data-tooltip").__contains__(key + ' ' + value):
                parent["data-tooltip"] = parent.get("data-tooltip") + '\n\n' + key + ' ' + value
            elif not parent.has_attr("data-tooltip"):
                parent["data-tooltip"] = key + ' ' + value
            else:
                break
    global regulation_body
    regulation_body = soup.body
    global regulation_with_annotations
    regulation_with_annotations = '<!DOCTYPE html><html lang="en"><head> <meta charset="UTF-8"> <title>Annotations' \
                                  '</title><style>[data-tooltip] {position: relative;}[data-tooltip]::after {content:' \
                                  'attr(data-tooltip);position: absolute; width: 600px; left: 0; top: 0; background: ' \
                                  '#3989c9; color: #fff; padding: 0.5em; box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.3); ' \
                                  'pointer-events: none; opacity: 0; transition: 1s; } [data-tooltip]:hover::after ' \
                                  '{opacity: 1; top: 2em; } </style></head>"' + str(regulation_body) + '</html>'
    format_document(soup)
    global relations
    relations = "\n".join(find_semantic_relations(annotations))


def find_title(s):
    start_class = s.find("p", string=re.compile("REGULATION"))
    end_class = s.find("p", string=re.compile("HE EUROPEAN PARLIAMENT AND THE COUNCIL"))
    title = str(start_class.text)
    for element in start_class.next_siblings:
        if element == end_class:
            break
        title = title + " " + element.text
    return title


# create a txt. file to download with all definitions and their explanations
def download_definitions_file(request):
    with open("file.txt", "w") as file:
        file.write(definitions)
    response = FileResponse(open("file.txt", 'rb'))
    response['Content-Disposition'] = 'attachment; filename="file.txt"'
    return response


# create a txt. file to download with all sentences with definitions
def download_sentences(request):
    with open("sentences.txt", "w") as file:
        sentences_set = get_sentences()
        for key, value in sentences_set.items():
            counter = get_counter()
            file.write("Definition: " + key + "\n")
            file.write("Total number of sentences including definition: " + str(counter[key]) + "\n\n")
            file.write(calculate_the_frequency(key) + "\n\n")
            file.write("\t\t" + value + "\n\n")
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
    response = FileResponse(open("relations.txt", 'rb'))
    response['Content-Disposition'] = 'attachment; filename="relations.txt"'
    return response
