from django import forms

class ContactForm(forms.Form):
    html_content = forms.CharField(widget=forms.Textarea)
