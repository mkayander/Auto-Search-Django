from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import User
from main.models import CarFilter, CarMark, CarModel

from main.widgets import MySelect

# class AuthUserForm(AuthenticationForm, forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'password')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'


# class RegisterUserForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ('username', 'password')

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password"])
#         if commit:
#             user.save()
#         return user

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs['class'] = 'form-control'

class FilterForm(forms.ModelForm):
    # cities = forms.CharField(max_length=100)
    # carname_mark = forms.CharField(max_length=30)
    # carname_model = forms.CharField(max_length=30)
    # hull = forms.CharField(max_length=20)
    # fuel = forms.CharField(max_length=20)
    # transm = forms.CharField(max_length=20)
    # radius = forms.IntegerField()
    # price_from = forms.IntegerField()
    # price_to = forms.IntegerField()
    # year_from = forms.IntegerField()
    # year_to = forms.IntegerField()
    # engine_from = forms.IntegerField()
    # engine_to = forms.IntegerField()

    mark_choice = forms.ModelChoiceField(queryset=CarMark.objects.all())

    mark_choice.label = 'Марка'

    model_choice = forms.ModelChoiceField(queryset=CarModel.objects.all(),
                                          to_field_name="name",
                                          widget=MySelect(attrs={'data-chained':'name'}))
    model_choice.label = 'Модель'

    class Meta:
        model = CarFilter
        #fields = '__all__'
        fields = ['cities', 'mark_choice', 'model_choice', 'hull', 'fuel', 'transm', 'radius', 'price_from', 'price_to', 'year_from', 'year_to', 'engine_from', 'engine_to']
