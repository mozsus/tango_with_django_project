from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page

def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    category_list = Category.objects.order_by('-likes')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    context_dict = {'author':'This tutorial has been put together by mooz.'}
    return render(request, 'rango/about.html', context=context_dict)

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass to the
    # template rendering engine.
    context_dict = {}

    try:
        # The .get() method returns one model instance 
        # or raises a DoesNotExist exception
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects 
        # or an empty list.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context 
        # under name pages.
        context_dict['pages'] = pages

        # We also add the category object from
        # the database to the context dicitionary
        # We'll use this in template to verify that the
        # category exists.
        context_dict['category'] = category

    except Category.DoesNotExist:
        # Don't do anything - the template will display
        # the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)