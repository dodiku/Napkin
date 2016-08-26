from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.db.models import Min, Count
from napkin.forms import GroupForm, PostForm, EmailForm
from napkin.models import Group, Post, Subscriber
from django.template.defaultfilters import slugify
import datetime
from time import strftime
from random_name import get_name
# from goose import Goose
from newspaper import Article
import tldextract
from operator import itemgetter
# from django.utils import timezone


env_url = "http://www.thisisnapkin.com/"
# env_url = "http://127.0.0.1:8000/"


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

        # getting recent groups
        if 'recent_groups' in request.session:
            recent_groups = request.session['recent_groups']
        else:
            recent_groups = 'none'

        # context dictionery
        context_dict = {
        'popular_groups': popular_groups,
        'recent_groups': recent_groups,
        'form': GroupForm(), # creating an empty form
        }

    return render(request, 'napkin/index.html', context_dict)


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


    # adding group to cookie for 'recently visited'

    request.session['built_on'] = 'green crack sativa'

    group_cookie = {
    "name": group_name,
    "url": env_url + group_name_slug,
    }

    if 'recent_groups' in request.session:
        if group_cookie in request.session['recent_groups']:
            request.session['recent_groups'].remove(group_cookie)
            request.session['recent_groups'].insert(0, group_cookie)
        else:
            request.session['recent_groups'].insert(0, group_cookie)

        cookie_length = len(request.session['recent_groups'])
        if cookie_length > 5:
            del request.session['recent_groups'][5]

    else:
        request.session['recent_groups'] = []
        request.session['recent_groups'].insert(0, group_cookie)

    email_form = EmailForm()


    context_dict = {
    'group_name_slug': group_name_slug,
    'group_id': group_id,
    'group_name': group_name,
    'posts': posts,
    'post_count': post_count,
    'created_date': first_post_date,
    'post_form': post_form,
    'group_form': group_form,
    'email_form': email_form,
    }

    return render(request, 'napkin/group_page.html', context_dict)

def post_click(request, click_id):
    post_object = Post.objects.get(id=click_id)
    post_object.hits = post_object.hits + 1
    post_object.save()

    return HttpResponse("post was received succesfully")

def post_click_redirect(request, click_id):
    post_object = Post.objects.get(id=click_id)
    post_object.hits = post_object.hits + 1
    post_object.save()

    redirection_url = post_object.url
    return redirect(redirection_url)

def email_subscriber(request, group_name_slug):

    print ('in email_subscriber')
    print (group_name_slug)

    try:
        group_object = Group.objects.get(name_slug=group_name_slug)
    except Group.DoesNotExist:
        return HttpResponse("Could not find the requested group. Subscription failed.")
        print ("bad 01")

    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            subscriber = form.save(commit=False)
            email = subscriber.email
            print (email)
            if Subscriber.objects.filter(email=email).count() == 0:
                new_subscriber = Subscriber(email=email)
                new_subscriber.save()
                group_object.subscribers.add(new_subscriber)
                print ("done - new subscriber")
                # return render(request, 'napkin/subscribe.html')
                # return HttpResponse("Subscription was done succesfully")
            else:
                old_subscriber = Subscriber.objects.get(email=email)
                group_object.subscribers.add(old_subscriber)
                print ("done - old subscriber")
                # return render(request, 'napkin/subscribe.html')
                # return HttpResponse("Subscription was done succesfully")

            context_dict = {
            'group_name': group_object.name,
            'return_url': env_url + group_name_slug,
            'email': email,
            }

            return render(request, 'napkin/subscribe.html', context_dict)

        else:
            print "email form is NOT valid --"
            redirection_url = env_url+group_name_slug
            return redirect(redirection_url)
            #
            # print form.errors
            # # email_form = form


    else:
        return HttpResponse("Not a POST request")
        print ("bad 02")



def feedback(request):
    return render(request, 'napkin/feedback.html',)

def about(request):
    return render(request, 'napkin/about.html',)
