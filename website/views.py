from django.shortcuts import render, get_list_or_404, get_object_or_404, redirect
from website.models import Media, Product, Record
from website.selection_tools import replacement_picker, wrapper, product_url_builder
from website.forms import RegistrationForm, SignInForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http.response import HttpResponseRedirect
from django.http import HttpResponse, Http404

import os, json, logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def home(request):

    logger.info('New visitor', exc_info=True, extra={
        # Optionally pass a request and we'll grab any information we can
        'request': request,
    })
    
    var = {'title': "P10 - Plateforme pour Amateurs de Nutella"}
        
    return render(request, "home.html", var)

@login_required()
def myproducts(request):

    myrecords = Record.objects.filter(user__exact=request.user)
    # print(get_list_or_404(Record.objects.all()))
    myproducts = [record.substitute for record in myrecords] 
    my_products_wrapped = wrapper(myproducts)

    vars = {'title': "Mes produits",
            'myproducts': my_products_wrapped}

    return render(request, "my_products.html", vars)

def product(request):

    #Les infos sont envoyée depuis les liens sur les produits

    if request.method == "GET":
        
        product_name = request.GET.get("query")
        product = get_object_or_404(Product, pk=product_name)
        
        vars = {"title": "Fiche produit - {}".format(product_name),
                "product": product}

        return render(request, "product.html", vars)

def suggest(request):

    # Récupérer ce que le client a renvoyé

    query = request.GET.get("query") 
    
    # Le traiter (aller chercher dans la base ce qu'il faut)

    products = Product.objects.filter(product_name__istartswith=query).order_by('product_name', 'category')[0:8] 
    suggestions = [product.product_name for product in products]
    search_suggestions_js = json.dumps({"suggestions": suggestions}, ensure_ascii=False)

    # Renvoyer les données

    return HttpResponse(search_suggestions_js)

def results(request):
    
    # Record.objects.all().delete() #Suppression rapide. All obligatoire?

    query = request.GET.get('query').strip()
    product = get_list_or_404(Product, product_name__iexact=query)[0]
    
    if request.user.is_authenticated:
        substitutes = replacement_picker(product, 0, 6)
        substitutes_wrapped = wrapper(substitutes, user = request.user)

    else:
        substitutes = replacement_picker(product, 0, 6)
        substitutes_wrapped = wrapper(substitutes)

    product_wrapped = wrapper([product])[0]

    vars = {'title': "Remplacement du produit : {}".format(product),
            'product': product_wrapped,
            'substitutes_wrapped': substitutes_wrapped}
            
    return render(request, "results.html", vars)

def save(request):

    if request.method == 'POST':
        
        print("[retour viewfunc] données reçues:", request.POST.dict())

        user_request = request.POST.get("request")
        substitute = request.POST.get('substitute')
        user_obj = request.user

        if user_request == "save":
            
            try:
                
                substitute_obj = Product.objects.get(product_name=substitute)
                print("[retour viewfunc] Substitut trouvé:", substitute_obj)

                Record.objects.create(
                    user = user_obj,
                    substitute = substitute_obj
                )
                print("[retour viewfunc] Produit enregistré. Nombre d'objects dans record:", Record.objects.count())

                return HttpResponse("SaveOK")

            except:
                return HttpResponse("SaveError")

        if user_request == "unsave":
            
            try:
                
                substitute_obj = Product.objects.get(pk=substitute)

                Record.objects.filter(
                    user__exact=user_obj
                    ).filter(
                    substitute__exact=substitute_obj).delete()

                print("Nombre d'objects après delete:", Record.objects.count())
                    
                return HttpResponse("UnsaveOK")

            except:
                return HttpResponse("SaveError")

    else:
        raise Http404("Web ressource not found! Well excuuuuuuse us, your highness!")
    
def signup(request):
    
    if request.method == "POST":
        # print(request.POST.dict()) #Et ça marche : {'csrfmiddlewaretoken': '26jzicmx6iR3LxTY4AvA9Fsfw0ofgrKlcJSJqjrsDsHnRSFAm1s5ihKBNJiqfust', 'first_name': 'dd', 'last_name': 'dd', 'username': 'dd', 'mail': 'a@j.fr', 'password': 'rr'}
        
        User.objects.create_user(
            username = request.POST.get('username'),
            password = request.POST.get('password'),
            email = request.POST.get('mail'),
            first_name = request.POST.get('first_name'),
            last_name = request.POST.get('last_name')
        )

        # for user in User.objects.all():
        #     print(user)

        return redirect("/") #pas de retour utilisateur ? Avec redirect par exemple ? 

    var = {'title': "Inscrivez-vous",
          'form': RegistrationForm()}
    
    return render(request, "signup.html", var)

def signin(request):
    
    if request.user.is_authenticated:
        return redirect(reverse("myproducts"))

    else:   
        if request.method == "POST":
            form = AuthenticationForm(request, request.POST)  

            if form.is_valid():

                user_obj = authenticate(
                    username = form.cleaned_data["username"], 
                    password = form.cleaned_data["password"]
                    ) #test aaa, aaa

                login(request, user_obj)

                if request.user.is_authenticated:
                    # print("2 Vous êtes connecté en tant que: ", request.user)
                    return HttpResponseRedirect("/")

        else:
            form = AuthenticationForm(request)
        
        vars = {
            'title': "Connexion",
            'form' : form 
            }

        return render(request, "signin.html", vars)

@login_required()
def account(request):

    user = request.user

    user_data = {
        'username':user.username,
        'first_name':user.first_name,
        'last_name':user.last_name,
        'mail': user.email
        }

    vars = {
        'title': "Mon compte",
        'form': RegistrationForm(initial=user_data)
    }

    return render(request, "account.html", vars)

def logoutv(request):
    logout(request)
    return redirect(reverse("home"))

def legal(request):

    vars = {'title': "Mentions (pas très) légales"}

    return render(request, "legal.html", vars)
