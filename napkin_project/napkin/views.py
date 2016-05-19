from django.shortcuts import render, redirect, render_to_response
from django.http import HttpResponse
from django.db.models import Min
from napkin.forms import GroupForm, PostForm
from napkin.models import Group, Post
from django.template.defaultfilters import slugify


def index(request):

    if request.method == 'POST':
        form = GroupForm(request.POST)

        if form.is_valid():
            group = form.save(commit=False)
            group_name = group.name
            group.name_slug = slugify(group_name)
            group_name_slug = group.name_slug
            group.save()
            return group_page (request, group_name_slug)

        else:
            print form.errors

    else:
        form = GroupForm()
    return render(request, 'napkin/index.html', {'form': form})



def group_page(request, group_name_slug):

    try:
        group_object = Group.objects.get(name_slug=group_name_slug)
        group_id = group_object.id
        group_name = group_object.name
        # Post.objects.annotate(post_date=Min('created')).filter(group_id=group_id)
        # first_post = Post.objects.filter(group_id=group_id).first()
        # first_post_date = first_post.created

        posts = Post.objects.filter(group_id=group_id).order_by('created')
        first_post_date = posts[0].created

        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.group_id = group_id
                post.save()
                slug = group_object.name_slug
                return group_page(request, slug)
            else:
                print form.errors
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
