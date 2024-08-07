from django.contrib.auth.models import User
from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError

class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'box'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'box'}))
    profile_image = forms.ImageField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

        
class LogInForm(AuthenticationForm):
    username = forms.CharField(max_length=254, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", strip=False, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Prof
        fields = '__all__'
        exclude = ['work','slug']
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields= ['username','first_name','last_name','email'] 
        
class ProfForm(forms.ModelForm):
    class Meta:
        model = Prof
        fields = '__all__'
        exclude = ['slug']