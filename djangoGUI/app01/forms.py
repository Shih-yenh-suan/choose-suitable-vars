# forms.py
from django import forms


class VarlistForm(forms.Form):
    dv = forms.CharField(label='dv')
    iv = forms.CharField(label='iv')
    cv = forms.CharField(label='cv')
    fe = forms.CharField(label='fe')
    mod = forms.CharField(label='mod')
    symbol = forms.CharField(label='symbol')
    date = forms.CharField(label='date')
    dta_file = forms.FileField(label='Upload dta file')
