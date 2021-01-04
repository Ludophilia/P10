import os, json, logging

from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.http import HttpResponse, Http404

from website.models import Media, Product, Record
from website.selection_tools import replacement_picker, wrapper
from website.forms import RegistrationForm, SignInForm

logger = logging.getLogger(__name__)

def home(request):

    user_addr = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR')
    logger.info(f"New visitor: {user_addr}", exc_info=False, extra={'request': request,})
    
    context = {'title': "P10 - Plateforme pour Amateurs de Nutella"}
        
    return render(request, "home.html", context)

@login_required()
def myproducts(request):

    myrecords = Record.objects.filter(user__exact=request.user)
    myproducts = [record.substitute for record in myrecords] 
    products_wrapped = wrapper(myproducts, user=request.user)

    context = {'title': "Mes produits", 'products_wrapped': products_wrapped}

    return render(request, "my_products.html", context)

def product(request):

    if request.method == "GET":
        
        product_name = request.GET.get("query")
        product = get_object_or_404(Product, pk = product_name)
        product_wrapped = wrapper([product], user = request.user) if request.user.is_authenticated else wrapper([product])

        context = {"title": f"Fiche produit - {product_name}", 
                  "product_wrapped": product_wrapped[0]}

        return render(request, "product.html", context)

def suggest(request):

    query = request.GET.get("query") 
    
    products = Product.objects.filter(product_name__istartswith=query).order_by('product_name', 'category')[0:8] 
    suggestions = [product.product_name for product in products]
    search_suggestions_js = json.dumps({"suggestions": suggestions}, ensure_ascii=False)

    return HttpResponse(search_suggestions_js)

def results(request):
    
    product_name = request.GET.get('query').strip()
    product = get_object_or_404(Product, product_name__iexact=product_name)
    substitutes = replacement_picker(product, 0, 6)

    substitutes_wrapped = wrapper(substitutes, user = request.user) if request.user.is_authenticated else wrapper(substitutes) 
    product_wrapped = wrapper([product])[0]

    context = {'title': f"Remplacement du produit : {product}",
               'product': product_wrapped,
               'substitutes_wrapped': substitutes_wrapped}
            
    return render(request, "results.html", context)

def save(request):

    if request.method == 'POST':
        
        user_request = request.POST.get("request")
        substitute = request.POST.get('substitute')
        user_obj = request.user

        if user_request == "save":
            
            try:
                substitute_obj = Product.objects.get(product_name=substitute)
                Record.objects.create(user = user_obj, substitute = substitute_obj)

                return HttpResponse("SaveOK")

            except:
                return HttpResponse("SaveError")

        if user_request == "unsave":
            
            try:
                substitute_obj = Product.objects.get(pk=substitute)

                Record.objects.filter(user__exact=user_obj).filter(
                    substitute__exact=substitute_obj).delete()
                    
                return HttpResponse("UnsaveOK")

            except:
                return HttpResponse("SaveError")

    else:
        raise Http404("Web ressource not found.")
    
def signup(request):
    
    if request.method == "POST":
        
        User.objects.create_user(
            username = request.POST.get('username'),
            password = request.POST.get('password'),
            email = request.POST.get('mail'),
            first_name = request.POST.get('first_name'),
            last_name = request.POST.get('last_name')
        )

        return redirect("/")

    context = {'title': "Inscrivez-vous",
               'form': RegistrationForm()}
    
    return render(request, "signup.html", context)

def signin(request):
    
    if request.user.is_authenticated:
        return redirect(reverse("myproducts"))

    else:   
        if request.method == "POST":
            form = AuthenticationForm(request, request.POST)  

            if form.is_valid():
                login(request,form.user_cache)

                if request.user.is_authenticated:
                    return HttpResponseRedirect("/")

        else:
            form = AuthenticationForm(request)
        
        context = {'title': "Connexion",'form' : form}

        return render(request, "signin.html", context)

@login_required()
def account(request):

    user = request.user

    user_data = {
        'username':user.username,
        'first_name':user.first_name,
        'last_name':user.last_name,
        'mail': user.email
        }

    context = {
        'title': "Mon compte",
        'form': RegistrationForm(initial=user_data)
    }

    return render(request, "account.html", context)

def logoutv(request):
    logout(request)
    return redirect(reverse("home"))

def legal(request):

    context = {'title': "Mentions (pas très) légales"}

    return render(request, "legal.html", context)
