from website.models import Product, Record, Nutrition

def replacement_picker(product, index_start, index_end):

    if type(index_start) == int and type(index_end) == int:

        sugary_product_categories = ["Biscuits et gâteaux", "Barres Chocolats noirs", "Chocolats au lait",
        "Viennoiseries", "Pâtes à tartiner", "Confitures de fruits", "Céréales pour petit-déjeuner", 
        "Chocolats en poudre", "Jus de fruits", "Boissons gazeuses", "Pizzas", "Céréales préparées", 
        "Yaourts", "Crèmes dessert", "Compotes", "Glaces et sorbets", "Fruits en conserve"]

        sug_fields, fat_fields = (("nutrition__sugars_100g", "nutrition__saturated_fat_100g", "nutrition__salt_100g"), 
        ("nutrition__saturated_fat_100g", "nutrition__salt_100g", "nutrition__sugars_100g"))
        dyna_fields = sug_fields if product.category in sugary_product_categories else fat_fields

        substitute = Product.objects.filter(category__exact=product.category
                    ).order_by("nutrition__nutriscore", *dyna_fields)
    
        return substitute[index_start:index_end]
    
    else:
        raise TypeError("index_start et/ou index_end doivent être des int")


def wrapper(product_list, **extra_args):

    products = []
    check_save_status = lambda user_recordings: "Sauvegardé" if user_recordings > 0 else "Sauvegarder"   

    for product in product_list:

        keys = {"product": product}

        if "user" in extra_args:
            
            user_recordings = Record.objects.filter(user__exact=extra_args['user']).filter(substitute__exact=product).count()
            save_status = check_save_status(user_recordings)

            keys = {**keys, "status": save_status}

        products += [keys]

    return products
