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
        print "DEBUG"
        print form.data['name']
        name = form.data['name']
        print (name)
        if Group.objects.filter(name=name).count() > 0:
            existing_group = Group.objects.get(name=name)
            redirection_url = "http://127.0.0.1:8000/"+existing_group.name_slug
            return redirect(redirection_url)
        else:
            if form.is_valid():
                group = form.save(commit=False)
                print "DEBUG"
                print (group)
                group.name_slug = slugify(group.name)
                group.created = datetime.datetime.now()
                print "DEBUG"
                print (group)
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
        group_id = group_object.id
        print (group_id)
        # pprint.pprint (group_object)
        print (Group.objects.filter(name_slug=group_name_slug).values())
        group_name = group_object.name
        print (group_name)
        # Post.objects.annotate(post_date=Min('created')).filter(group_id=group_id)
        # first_post = Post.objects.filter(group_id=group_id).first()
        # first_post_date = first_post.created

        posts = Post.objects.filter(group_id=group_id).order_by('-created')
        print "post object --"
        print (Post.objects.filter(group_id=group_id).order_by('-created').values())
        print "post object datetime.now() --"
        print (datetime.datetime.now())
        if not posts:
            first_post_date = "This Napkin is empty."
        else:
            first_post = Post.objects.filter(group_id=group_id).order_by('-created').first()
            first_post_date_unformated = first_post.created
            first_post_date = "Since " + first_post_date_unformated.strftime("%B %d, %Y")

        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.group_id = group_id
                post.save()
                slug = group_object.name_slug
                return render('napkin/group_page.html')
            else:
                print form.errors.as_data()
        else:
            context_dict = {
            'group_name': group_name,
            'created_date': first_post_date,
            'posts': posts,
            'form': PostForm(),
            }

    except Group.DoesNotExist:
        return redirect('/')

    return render_to_response('napkin/group_page.html', context_dict)
