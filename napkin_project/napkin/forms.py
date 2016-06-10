from django import forms
from django.template.defaultfilters import slugify
from napkin.models import Group, Post
from random_name import get_name
from django.core.exceptions import ValidationError


def generate_name():
    for i in range(1, 10):
        name = get_name()
        if not Group.objects.filter(name=name).first():
            return name

random_name = generate_name()

class GroupForm(forms.ModelForm):
    name = forms.CharField(max_length=24, help_text=(random_name + "..."), initial=random_name)
    # name_slug = forms.CharField(widget=forms.HiddenInput(), required=False) ### excluded
    # created = forms.DateTimeField(widget=forms.HiddenInput(), required=False) ### excluded

    class Meta:
        model = Group
        exclude = ('name_slug', 'created',)



class PostForm(forms.ModelForm):
    # group = forms.ForeignKey(widget=forms.HiddenInput()) ### excluded
    url = forms.URLField(required=False, help_text="url...")
    text = forms.CharField(required=False, max_length=1000, help_text="write a comment...")
    # created = forms.DateTimeField(widget=forms.HiddenInput(), required=False, initial=0) ### excluded

    class Meta:
        model = Post
        exclude = ('group', 'created',)

    def clean(self):
        if self.cleaned_data.get('url') and not self.cleaned_data.get('url').startswith("http://"):
            url = "http://" + self.cleaned_data.get('url')
            self.cleaned_data['url'] = url
        return self.cleaned_data
