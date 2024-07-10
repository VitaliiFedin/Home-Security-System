from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Apartment, Building, Entrance, User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("role",)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class BuildingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter the queryset for managers
        self.fields["manager"].queryset = User.objects.filter(role=User.MANAGER)

    class Meta:
        model = Building
        fields = ["number", "manager"]


class EntranceForm(forms.ModelForm):
    class Meta:
        model = Entrance
        fields = ["number", "guard", "building"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["guard"].queryset = User.objects.filter(role=User.GUARD)


class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = "__all__"


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
