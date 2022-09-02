from django import forms

class KakikomiForm(forms.Form):
     year = forms.IntegerField()
     month = forms.IntegerField() 