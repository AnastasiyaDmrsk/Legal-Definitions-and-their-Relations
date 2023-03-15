# Identification and Visualization of Legal Definitions and their Relations Based on European Regulatory Document
***
The goal of this project is to implement a prototype capable of extracting legal definitions from Regulations of the European Parliament and of the Council in the English Language provided by [EUR-Lex](https://eur-lex.europa.eu) and identifying semantic relations among them. The tool operates exactly one regulatory document, which corresponds to the CELEX number entered by the user. 
## General Information
***
This project concentrates on three main assignments: information retrieval in form of definitions, attaching annotations to the collected document, extracting text segments containing legal terms, and building semantic relations among definitions such as hyponymy and synonymy. The intention is to facilitate the understanding of regulatory documents and accelerate the search of relevant information in legal text. 

### Definitions Extraction
The extraction of legal term is implemented with the support of BeautifulSoup HTML parser and spaCy NLP techniques like tokenization, POS tagging, and dependency parsing. For assigning annotations and storing text segments mentioning legal definitions, we applied BeautifulSoup and rewrote the content of detected sentences with a new data-tooltip tag. 

### Relations Extraction 
With the purpose of identifying semantic relations among legal definitions, such as hyponymy, we apply SpaCy and iterate over each term's explanation searching for the noun phrases. In the presented approach we consider M:N relationships as well, where many definitions can have many explanations and so many hypernyms. On the other hand, M:1 relationship points to the synonymy, which is also handled by the prototype. 

### Vizualization 
To design a layout of the prototype, we applied Django Forms and Bootstrap. A user is supposed to submit a valid CELEX of a regulation containing an article "Definitions", otherwise a validation error is raised with an individual message depending on the problem. If the regulation passes the criteria, the prototype handles the document and redirects users to the resulting page. With the purpose of increasing usability, the tool extracts the full title of the entered regulation. Additionally, it displays five options: the user can be redirected to the original source in EUR-Lex or download all the generated output files in the specified format. Furthermore, the prototype renders the statistics relying on the regulation, such as the date of execution and the number of legal definitions, together with more specific statistics referring to the extracted definitions, such as the most frequent definitions and the number of articles where they occur. 

## Technologies
***
A list of technologies used within the project:
* PyCharm (https://www.jetbrains.com/de-de/pycharm/): Version 2021.2.3
* Python (https://www.python.org/): Version 3.10.0
* BeautifulSoup (https://beautiful-soup-4.readthedocs.io/en/latest/)
* spaCy (https://spacy.io)
* WordNet (https://wordnet.princeton.edu)
* NLTK (https://www.nltk.org)
* Django (https://www.djangoproject.com/): Version 3.2.9
* HTML (https://dev.w3.org/html5/): Version 5.0
* CSS (https://www.w3.org/Style/CSS/)
* Bootstrap (https://getbootstrap.com/): Version 5.1.3
## Installation
***
1. Clone a remote repository 
```bash
git clone git@github.com:AnastasiyaDmrsk/Identification-and-Visualization-of-Legal-Definitions-and-Relations.git
```
2. Go into the project directory
```bash
cd Identification-and-Visualization-of-Legal-Definitions-and-Relations
```
3. In case you have already cloned the repository before use:
```bash
git pull
```
4. Install all project dependencies with the help of the package manager [pip](https://pip.pypa.io/en/stable/)
```bash
pip install -r requirements.txt
```
5. Go into the mysite directory 
```bash
cd src
```
6. Run the server (locally)
```bash
python manage.py runserver
```
Enjoy!

