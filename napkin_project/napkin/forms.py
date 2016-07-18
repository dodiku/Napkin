from django import forms
from django.template.defaultfilters import slugify
from napkin.models import Group, Post
from random_name import get_name
from django.core.exceptions import ValidationError


my_default_errors = {
    'invalid': 'Please enter a valid URL.'
}

def generate_name():
    for i in range(1, 10):
        name = get_name()
        if not Group.objects.filter(name=name).first():
            return name

class GroupForm(forms.ModelForm):
    name = forms.CharField(required=False, max_length=24, help_text=(lambda x: generate_name() + '...'), widget=forms.TextInput({ "placeholder": "enter group name..."}))
    # name_slug = forms.CharField(widget=forms.HiddenInput(), required=False) ### excluded
    # created = forms.DateTimeField(widget=forms.HiddenInput(), required=False) ### excluded

    class Meta:
        model = Group
        exclude = ('name_slug', 'created',)

    # def clean(self):
    #     if self.cleaned_data.get('name') == "":
    #         print "=== got empty form for group ==="
    #         self.cleaned_data['name'] = random_name
    #         self.cleaned_data['name_slug'] = slugify(random_name)
    #         print "*** clean ***"
    #         a = self.cleaned_data['name']
    #         b = self.cleaned_data['name_slug']
    #         print a
    #         print b
    #         print "*** clean ***"
    #     return self.cleaned_data



class PostForm(forms.ModelForm):
    # group = forms.ForeignKey(widget=forms.HiddenInput()) ### excluded
    url = forms.URLField(required=False, help_text="url...", widget=forms.TextInput({ "placeholder": "url..."}), error_messages=my_default_errors)
    text = forms.CharField(required=False, max_length=1000, help_text="write a comment...", widget=forms.Textarea({ "placeholder": "write a comment..."}))
    # created = forms.DateTimeField(widget=forms.HiddenInput(), required=False, initial=0) ### excluded

    class Meta:
        model = Post
        exclude = ('group', 'created',)

    def clean(self):
        if self.cleaned_data.get('url') and not (self.cleaned_data.get('url').startswith("http://") or self.cleaned_data.get('url').startswith("https://")):
            url = "http://" + self.cleaned_data.get('url')
            self.cleaned_data['url'] = url
        return self.cleaned_data
