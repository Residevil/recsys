from .models import User, Business, Review
from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class GenerateRandomUserForm(forms.Form):
    total = forms.IntegerField(
        validators=[
            MinValueValidator(50),
            MaxValueValidator(500)
        ]
    )

class RegisterForm(UserCreationForm):   
    email = forms.EmailField(max_length=254)
 
    class Meta:
        model = get_user_model() #models.User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    # email = forms.EmailField(max_length=254)
    username = forms.CharField(max_length=65)
    password = forms.CharField(label=("Password"), max_length= 65, strip=False, widget=forms.PasswordInput)
    
    class Meta:
        model = get_user_model() #models.User
        fields = ('email', 'username', 'password')

# class PasswordChangeForm(forms.Form):
#     email = forms.EmailField(max_length=254)
#     class Meta:
#         model = get_user_model() #models.User
#         fields = ('email', 'username', 'old_password' 'new_password1', 'new_password2')

class PasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=254)
    class Meta:
        model = User #models.User
        fields = ('email', 'username', 'old_password' 'new_password1', 'new_password2')