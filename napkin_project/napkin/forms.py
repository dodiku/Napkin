from django import forms
from django.template.defaultfilters import slugify
from napkin.models import Group, Post
from random_name import get_name

def generate_name():
    for i in range(1, 10):
        name = get_name()
        if not Group.objects.filter(name=name).first():
            return name

random_name = generate_name()

class GroupForm(forms.ModelForm):
    name = forms.CharField(max_length=24, help_text=(random_name + "..."), initial=random_name)
    name_slug = forms.CharField(widget=forms.HiddenInput(), required=False)
    created = forms.DateTimeField(widget=forms.HiddenInput(), required=False, initial=0)

    class Meta:
        model = Group
        fields = ('name',)


class PostForm(forms.ModelForm):
    # group_id = forms.ForeignKey(widget=forms.HiddenInput()) ### excluded
    url = forms.URLField(required=False, help_text="url...")
    text = forms.CharField(max_length=1000, required=True, help_text="write a comment...")
    created = forms.DateTimeField(widget=forms.HiddenInput(), required=False, initial=0)

    class Meta:
        model = Post
        exclude = ('group_id',)
