from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.db.models import Min
from napkin.forms import GroupForm, PostForm
from napkin.models import Group, Post
from django.template.defaultfilters import slugify
import datetime
from time import strftime
from random_name import get_name
# from goose import Goose
from newspaper import Article
import tldextract


def generate_name():
    for i in range(1, 10):
        name = get_name()
        if not Group.objects.filter(name=name).first():
            return name


def index(request):

    if request.method == 'POST':
        form = GroupForm(request.POST)

        print "DEBUG index view"
        print form.data['name']
        name = form.data['name']
        name_slug = slugify(name)
        print name_slug
        if Group.objects.filter(name_slug=name_slug).count() > 0 and name != "":
            redirection_url = "http://127.0.0.1:8000/"+name_slug
            return redirect(redirection_url)
        else:
            if form.is_valid():
                group = form.save(commit=False)
                if group.name == "":
                    print "doing something with the missing name..."
                    random_name = generate_name()
                    print random_name
                    group.name = random_name
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

    post_form = PostForm()
    group_form = GroupForm()

    if request.method == 'POST':

        if 'url' in request.POST:
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                #
                #     # title = models.CharField(blank=True) // post.title
                #     # home_url = (blank=True) // post.home_url
                #
                # print "post url:"
                # print post.url
                # print "post text:"
                # print post.text
                # print "=== THIS IS NEWSPAPER: START ==="
                #
                # print ""
                # article = Article(post.url)
                # article.download()
                # article.parse()
                # print "title:"
                # print(article.title)
                # # print ""
                # # print "text:"
                # # print(article.text)
                # # print ""
                #
                # print "=== THIS IS NEWSPAPER: END ==="
                # print ""
                # print ""
                #
                #
                # print "=== THIS IS tldextract: START ==="
                #
                # brand = tldextract.extract(post.url)
                # brand = brand.registered_domain
                # print brand
                # brand = "http://www." + brand
                # print brand
                #
                #
                # print "=== THIS IS tldextract: END ==="


                if post.url or post.text:
                    post.group = group_object
                    post.created = datetime.datetime.now()

                    if post.url:
                        # getting article title using newspaper
                        article = Article(post.url)
                        article.download()
                        article.parse()
                        if article.title:
                            post.title = article.title
                        else:
                            post.title = post.url
                        print "post title:"
                        print post.title

                        # getting homepage name and url using tldextract
                        site_name = tldextract.extract(post.url)
                        site_name = site_name.registered_domain
                        post.site_name = site_name

                        site_url = "http://www." + site_name
                        post.site_url = site_url
                        print "home url:"
                        print post.site_url

                    post.save()

                redirection_url = "http://127.0.0.1:8000/"+group_name_slug
                return redirect(redirection_url)

            else:
                print "post form is NOT valid --"
                print form.errors
                post_form = form
        else:
            form = GroupForm(request.POST)
            print "DEBUG index view"
            print form.data['name']
            name = form.data['name']
            name_slug = slugify(name)
            print name_slug
            if Group.objects.filter(name_slug=name_slug).count() > 0 and name != "":
                redirection_url = "http://127.0.0.1:8000/"+name_slug
                return redirect(redirection_url)
            else:
                if form.is_valid():
                    group = form.save(commit=False)
                    if group.name == "":
                        print "doing something with the missing name..."
                        random_name = generate_name()
                        print random_name
                        group.name = random_name
                    group.name_slug = slugify(group.name)
                    group.created = datetime.datetime.now()
                    group.save()
                    redirection_url = "http://127.0.0.1:8000/"+group.name_slug
                    return redirect(redirection_url)

                else:
                    ## DEBUG
                    print "form is NOT valid"
                    print " "

                    group_form = form

    group_id = group_object.id
    group_name = group_object.name

    posts = Post.objects.filter(group_id=group_id).order_by('-created')
    if not posts:
        first_post_date = "This Napkin is empty."
    else:
        first_post = Post.objects.filter(group_id=group_id).order_by('-created').first()
        first_post_date_unformated = first_post.created
        first_post_date = "Since " + first_post_date_unformated.strftime("%B %d, %Y")

    context_dict = {
    'group_name_slug': group_name_slug,
    'group_id': group_id,
    'group_name': group_name,
    'posts': posts,
    'created_date': first_post_date,
    'post_form': post_form,
    'group_form': group_form,
    }

    return render(request, 'napkin/group_page.html', context_dict)


def feedback(request):
    return render(request, 'napkin/feedback.html',)

def about(request):
    return render(request, 'napkin/about.html',)
