from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.db.models import Min, Count
from napkin.forms import GroupForm, PostForm
from napkin.models import Group, Post
from django.template.defaultfilters import slugify
import datetime
from time import strftime
from random_name import get_name
# from goose import Goose
from newspaper import Article
import tldextract
from operator import itemgetter
# from django.utils import timezone


# env_url = "http://www.thisisnapkin.com/"
env_url = "http://127.0.0.1:8000/"


def generate_name():
    for i in range(1, 10):
        name = get_name()
        if not Group.objects.filter(name=name).first():
            return name


def index(request):

    request.session.set_test_cookie()

    if request.method == 'POST':
        form = GroupForm(request.POST)

        print "DEBUG index view"
        print form.data['name']
        name = form.data['name']
        name_slug = slugify(name)
        print name_slug
        if Group.objects.filter(name_slug=name_slug).count() > 0 and name != "":
            redirection_url = env_url+name_slug
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
                redirection_url = env_url+group.name_slug
                return redirect(redirection_url)

            else:
                ## DEBUG
                print "form is NOT valid"
                print " "
                print form.errors.as_data()

    else:

        # creating a list of dictioneries that includes the names of the groups and the number of new posts
        popular_groups = []
        all_groups = Group.objects.all()
        last_month = datetime.datetime.today()-datetime.timedelta(days=30)

        i = 0
        for item in all_groups:
            postCount = Post.objects.filter(created__gt=last_month, group=item.id).aggregate(Count('group'))
            postCount = postCount['group__count']
            if postCount != 0:
                obj = {
                'name': all_groups[i].name,
                'url': env_url + all_groups[i].name_slug,
                'post_count': postCount,
                }
                popular_groups.append(obj)
            i = i + 1

        # soring the list by post_count
        popular_groups = sorted(popular_groups, key=itemgetter('post_count'), reverse=True)
        popular_groups = popular_groups[:5]
        print (popular_groups)

        # context dictionery
        context_dict = {
        'popular_groups': popular_groups,
        'form': GroupForm(), # creating an empty form
        }

    return render(request, 'napkin/index.html', context_dict)


def group_page(request, group_name_slug):

    if request.session.test_cookie_worked():
        print ">>>> TEST COOKIE WORKED!"
        request.session.delete_test_cookie()

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
                        # print "post title:"
                        # print post.title

                        # getting homepage name and url using tldextract
                        site_name = tldextract.extract(post.url)
                        site_name = site_name.registered_domain
                        post.site_name = site_name

                        site_url = "http://www." + site_name
                        post.site_url = site_url
                        print "home url:"
                        print post.site_url

                    post.save()

                redirection_url = env_url+group_name_slug
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
                redirection_url = env_url+name_slug
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
                    redirection_url = env_url+group.name_slug
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
        post_count = 0

    else:
        first_post = Post.objects.filter(group_id=group_id).order_by('-created').first()
        first_post_date_unformated = first_post.created
        first_post_date = "Since " + first_post_date_unformated.strftime("%B %d, %Y")

        # getting number of posts in group_id
        post_count = Post.objects.filter(group_id=group_id).count()
        print post_count

    context_dict = {
    'group_name_slug': group_name_slug,
    'group_id': group_id,
    'group_name': group_name,
    'posts': posts,
    'post_count': post_count,
    'created_date': first_post_date,
    'post_form': post_form,
    'group_form': group_form,
    }

    return render(request, 'napkin/group_page.html', context_dict)


def feedback(request):
    return render(request, 'napkin/feedback.html',)

def about(request):
    return render(request, 'napkin/about.html',)
