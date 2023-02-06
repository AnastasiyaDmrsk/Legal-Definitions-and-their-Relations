from django import forms
from django.core.exceptions import ValidationError


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
            raise ValidationError('The year of a regulation is invalid')
    elif celex[5] != 'R':
        raise ValidationError('The legislation has to be a regulation.')


class FormCELEX(forms.Form):
    number = forms.CharField(label='Please enter a CELEX number of a regulation', min_length=10,
                             max_length=10, validators=[check])
