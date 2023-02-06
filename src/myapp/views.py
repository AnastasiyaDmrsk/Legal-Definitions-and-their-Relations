import os

from django.shortcuts import render
from .forms import FormCELEX
from django.http import HttpResponse, HttpResponseRedirect
import requests
import re
from bs4 import BeautifulSoup
from django.http import FileResponse
from myapp.relations_spacy import find_semantic_relations

site = ""
celex = ""
reg_title = ""
definitions = ""
sentences_with_definitions = ""
sentences_set = {}
annotations = {}
regulation_with_annotations = ""
done_date = ""
counter_set = {}  # counts the frequency of each definition


def index(request):
    if request.method == 'POST':
        form = FormCELEX(request.POST)

        if form.is_valid():
            global celex
            celex = form.cleaned_data['number']
            global site
            site = load_document(celex)
            return HttpResponseRedirect('result/')
            # return HttpResponseRedirect(site)
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


# soup.find("tag_name", {"class":"class_name"}) for specific information
def extract_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    global reg_title
    reg_title = find_title(soup)
    find_definitions(soup)
    global done_date
    done_date = soup.find(string=re.compile("Done at"))
    # add annotations to the existing regulation
    global annotations
    for key, value in annotations.items():
        # global sentences_with_definitions
        sentences = soup.find_all(string=lambda text: key in text)
        # sentences_with_definitions = sentences_with_definitions + "\n" + key
        for sentence in sentences:
            # sentences_with_definitions = "\n" + sentence.text
            # Add the annotation as a new attribute to the parent element of the text
            parent = sentence.parent
            parent["data-annotation"] = value
    # Save a regulation with annotations
    global regulation_with_annotations
    regulation_with_annotations = str(soup)
    format_document(soup)
    # semantic relations
    global definitions
    # find_semantic_relations(annotations)
    # return definitions


def find_title(s):
    title = ""
    doc_title = s.find_all("p", {"class": "doc-ti"})
    for element in doc_title:
        title = title + " " + element.text
    return title


def find_definitions(soup):
    defin = []
    # extract only the article which contains definitions
    start_class = soup.find("p", {"class": "sti-art"}, string="Definitions")  # {"id": "d1e1489-1-1"}
    end_class = soup.find("p", {"class": "ti-art"}, string=re.compile("Article"))  # d1e1797-1-1
    # extract the definitions and their explanations
    for element in start_class.next_siblings:
        if element == end_class:
            break
        if element.text.__contains__("’") & element.text.__contains__("means"):
            full_def = element.text.replace("\n\n", "\n")
            only_def = full_def.split("’")[0].strip()
            # extracting concrete definitions and explanations for later search as a dictionary
            match = re.search("[a-zA-Z]", only_def)
            if match:
                only_def = only_def[match.start():]
                stringtosplit = only_def + '’ '
                only_expl = full_def.split(stringtosplit)[1].strip()
                # add an annotation to the dictionary
                global annotations
                annotations[only_def] = only_expl
            defin.append(full_def.replace("\n\n", "\n"))
    global definitions
    definitions = "".join(defin)


def format_document(s):
    global counter_set
    global sentences_set
    # leaving only enacting terms
    start_class = s.find("p", {"class": "normal"}, string="HAVE ADOPTED THIS REGULATION:")
    end_class = s.find("div", {"class": "final"})
    for key, value in annotations.items():
        counter = 0
        all_sentences = ""
        for element in start_class.next_siblings:
            if element == end_class:
                break
            if key in element.text:
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
        global sentences_set
        for key, value in sentences_set.items():
            file.write("Definition: " + key + "\n")
            file.write("Total number of sentences including definition: " + str(counter_set[key]) + "\n\n")
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
