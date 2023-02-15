from django import forms
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
import requests


# documentation how CELEX is identified: https://eur-lex.europa.eu/content/tools/eur-lex-celex-infographic-A3.pdf
# first char is a sector (in our case for regulations it should be 3)
# 2.-5. char is a year
# 6. char should be R for regulation
# 7.-10. char is a document number
def check(celex):
    if celex[0] != '3':
        raise ValidationError('The sector has to be 3, which stays for a legislation.')
    elif celex[1] != '1':
        if celex[1] != '2':
            raise ValidationError('The year of a regulation is invalid. ')
    elif celex[5] != 'R':
        raise ValidationError('The legislation has to be a regulation. ')
    # check whether the regulation exists or not
    new_url = 'https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:' + celex + '&from=EN'
    soup = BeautifulSoup(requests.get(new_url).text, 'html.parser')
    if soup.find('title').getText().__contains__("The requested document does not exist"):
        raise ValidationError('The entered CELEX does not exist. ')
    # check whether a regulation contains a chapter definitions or not
    if soup.find("p", string="Definitions") is None:
        raise ValidationError('The regulation does not contain legal definitions and cannot be processed. ')


class FormCELEX(forms.Form):
    number = forms.CharField(label='Please enter a CELEX number of a regulation', min_length=10,
                             max_length=10, validators=[check])
