from django import forms
from django.contrib.auth.forms import AuthenticationForm

class RegistrationForm(forms.Form):
    first_name = forms.CharField(label='Prenom', max_length=50)
    last_name = forms.CharField(label='Nom', max_length=50)
    username = forms.CharField(label='Pseudo', max_length=50)
    mail = forms.EmailField(label='Mail', max_length=50)
    password = forms.CharField(label='Mot de passe', max_length=50, widget=forms.PasswordInput())

class SignInForm(forms.Form):
    username = forms.CharField(label='Pseudo', max_length=50)
    password = forms.CharField(label='Mot de passe', max_length=50, widget=forms.PasswordInput())

class AuthenticationFormPlus(AuthenticationForm):
    error_css_class = 'invalid-feedback' #marche pas, sans doute parce qu'il faut hériter de forms.Form
