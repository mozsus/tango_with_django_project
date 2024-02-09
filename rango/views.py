from django.shortcuts import render, redirect
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime

def index(request):
    # Construct a dictionary to pass to the template engine as its context.
    # Note the key boldmessage matches to {{ boldmessage }} in the template!
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # Call the helper function to handle the cookies.
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    # [depr_code] return render(request, 'rango/index.html', context=context_dict)
    
    # Obtain our Response object early so we can add cookie information.
    response = render(request, 'rango/index.html', context=context_dict)

    # Return response back to the user, updating any cookie changes.
    return response

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

@login_required
def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            # Save the new category to the database.
            cat = form.save(commit=True)

            print(cat, cat.slug)
            
            # Redirect the user back to the index view
            return redirect('/rango/')
        else:
            # The supplied form contained errors -
            # just print them to the terminal
            print(form.errors)

    # Will handle bad form, new form, or no form supplied cases
    # Render the form with error messages (if any)
    return render(request, 'rango/add_category.html', {'form':form})

@login_required
def add_page(request, category_name_slug):

    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # You cannot ade a page to a Category that does not exist
    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', 
                                        kwargs={'category_name_slug':category_name_slug}))
            
        else:
            print(form.errors)
    
    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    # A boolean value for telling the template whether
    # the registration was successful.
    # Set to False initially. Code changes value to True
    # when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with set_password method.
            # Once hashed, we can upadte the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out UserProfile instance.
            profile = profile_form.save(commit=False)
            profile.user = user

            # Get profile picture from the input form and put it 
            # in the UserProfile model
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Save the UserProfile model instance.
            profile.save()

            # Update our variable to indicate that the template
            # registration was successful
            registered = True
        
        else:
            # Invalid form
            # Print problems to the terminal
            print(user_form.errors, profile_form.errors)
    
    else:
        # Not a HTTP POST, so we render our form using 
        # two ModelForm instances.
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request, 'rango/register.html', context={'user_form': user_form,
                                                           'profile_form': profile_form,
                                                           'registered': registered })

def user_login(request):
    # If request is a HTTP POST, pull out relevant information.
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None, no user with matching credentials found.
        if user:
            # Check if account active or disabled.
            if user.is_active:
                # If account valid and active, we can log the user in.
                # Send user back to homepage.
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # Inactive account - no logging in
                return HttpResponse("Your Rango account is disabled.")
        
        else:
            # Bad login details were provided. Can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied")
        
    # The request is not HTTP POST, so display login form.
    # This scenario is a HTTP GET
    else:
        # No context variables to pass, hence blank dictionary. 
        return render(request, 'rango/login.html')
    
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

# Helper method: 

# -- Server-side Cookie --
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# -- Cookie Handler --
def visitor_cookie_handler(request):
    # Get the number of visits to the site.
    # Use COOKIES.get() to obtain visits cookie.
    # If cookie exist, the value returned is casted to an integer.
    # If not exist, then default value is 1.
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    # [TEST] Cookies elapsed test:
    #if (datetime.now() - last_visit_time).seconds > 0:
    
    # If it's been more than a day since last visit
    if (datetime.now() - last_visit_time).days > 0:
        visits += 1
        # Update the last visit cookie now
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie

    # Update/set the visits cookie
    request.session['visits'] = visits