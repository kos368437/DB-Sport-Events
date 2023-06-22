from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction


class SignUpForm(forms.Form):

    phone_number = forms.CharField(
        required=True,
        label="Номер телефона",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': "inputNumber",
            'placeholder': "Номер телефона",
        }),
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': "form-control",
            'id': "inputEmail",
            'placeholder': "Email",
        }),
    )

    surname = forms.CharField(
        required=True,
        label="Фамилия",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': "inputSurname",
            'placeholder': "Фамилия",
        }),
    )

    name = forms.CharField(
        required=True,
        label="Имя",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': "inputName",
            'placeholder': "Имя",
        }),
    )

    middle_name = forms.CharField(
        required=False,
        label="Отчество",
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': "inputMiddleName",
            'placeholder': "Отчество",
        }),
    )

    password = forms.CharField(
        required=True,
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'id': "inputPassword",
            'placeholder': "Пароль",
        }),
    )
    repeat_password = forms.CharField(
        required=True,
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={
            'class': "form-control",
            'id': "ReInputPassword",
            'placeholder': "Повторите пароль",
        }),
    )

    def clean(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['repeat_password']
        email = self.cleaned_data['email']

        user_check = User.objects.filter(email=email)
        if user_check.count() > 0:
            raise forms.ValidationError(
                "Пользователь с таким email уже зарегистрирован"
            )

        if password != confirm_password:
            raise forms.ValidationError(
                "Пароли не совпадают"
            )


    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
        )
        user.profile.phone_number = self.cleaned_data['phone_number']
        user.profile.name = self.cleaned_data['name']
        user.profile.surname = self.cleaned_data['surname']
        user.profile.middle_name = self.cleaned_data['middle_name']

        user.save()
        auth = authenticate(**self.cleaned_data)
        return auth

class SignInForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': "form-control",
            'id': "inputEmail",
            'placeholder': "Email",
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': "form-control mt-2",
            'id': "inputPassword",
            'placeholder': "Пароль",
        })
    )