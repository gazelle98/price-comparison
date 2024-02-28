from django import forms


class ItemForm(forms.Form):
    item_name = forms.CharField(max_length=200)