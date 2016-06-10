from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.db.models import Min
from napkin.forms import GroupForm, PostForm
from napkin.models import Group, Post
from django.template.defaultfilters import slugify
import datetime
from time import strftime

def index(request):

    if request.method == 'POST':
        form = GroupForm(request.POST)
        # create_or_redirect(form)
        print "DEBUG index view"
        print form.data['name']
        name = form.data['name']
        name_slug = slugify(name)
        print name_slug
        if Group.objects.filter(name_slug=name_slug).count() > 0:
            redirection_url = "http://127.0.0.1:8000/"+name_slug
            return redirect(redirection_url)
        else:
            if form.is_valid():
                group = form.save(commit=False)
                group.name_slug = slugify(group.name)
                group.created = datetime.datetime.now()
                group.save()
                redirection_url = "http://127.0.0.1:8000/"+group.name_slug
                return redirect(redirection_url)

            else:
                ## DEBUG
                print "form is NOT valid"
                print " "
                print form.errors.as_data()

    else:
        form = GroupForm()
    return render(request, 'napkin/index.html', {'form': form})


def group_page(request, group_name_slug):

    try:
        group_object = Group.objects.get(name_slug=group_name_slug)
    except Group.DoesNotExist:
        return redirect('/')

    group_id = group_object.id
    print "DEBUG group_page view"
    print "group_id:"
    print group_id

    if request.method == 'POST':

        if 'url' in request.POST:
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                print "post url:"
                print post.url
                print "post text:"
                print post.text
                if post.url or post.text:
                    post.group = group_object
                    post.created = datetime.datetime.now()
                    post.save()
                redirection_url = "http://127.0.0.1:8000/"+group_name_slug
                return redirect(redirection_url)
            else:
                print "post form is NOT valid --"
                print form.errors

        else:
            form = GroupForm(request.POST)
            print form.data['name']
            name = form.data['name']
            name_slug = slugify(name)
            print name_slug
            if Group.objects.filter(name_slug=name_slug).count() > 0:
                redirection_url = "http://127.0.0.1:8000/"+name_slug
                return redirect(redirection_url)
            else:
                if form.is_valid():
                    group = form.save(commit=False)
                    group.name_slug = slugify(group.name)
                    group.created = datetime.datetime.now()
                    group.save()
                    redirection_url = "http://127.0.0.1:8000/"+group.name_slug
                    return redirect(redirection_url)
                else:
                    print "group form is NOT valid --"
                    print form.errors.as_data()

        #
        # #
        # if Group.objects.filter(name_slug=name_slug).count() > 0:
        #     redirection_url = "http://127.0.0.1:8000/"+name_slug
        #     return redirect(redirection_url)
        # else:
        #     if form.is_valid():
        #         group = form.save(commit=False)
        #         group.name_slug = slugify(group.name)
        #         group.created = datetime.datetime.now()
        #         group.save()
        #         redirection_url = "http://127.0.0.1:8000/"+group.name_slug
        #         return redirect(redirection_url)
        #     else:
        #         print "group form is NOT valid --"
        #         print group_form.errors.as_data()

    group_name = group_object.name
    posts = Post.objects.filter(group_id=group_id).order_by('-created')

    if not posts:
        first_post_date = "This Napkin is empty."
    else:
        first_post = Post.objects.filter(group_id=group_id).order_by('-created').first()
        first_post_date_unformated = first_post.created
        first_post_date = "Since " + first_post_date_unformated.strftime("%B %d, %Y")

    context_dict = {
    'group_name': group_name,
    'created_date': first_post_date,
    'posts': posts,
    'post_form': PostForm(),
    'group_form': GroupForm(),
    'group_id': group_id,
    'group_name_slug': group_name_slug,
    }

    return render(request, 'napkin/group_page.html', context_dict)
