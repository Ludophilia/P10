from django.db import models

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=200, primary_key=True)
    off_url = models.TextField()
    category = models.CharField(max_length=200)

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = "product"

class Nutrition(models.Model):
    product = models.OneToOneField(Product, to_field="product_name", primary_key = True, on_delete = models.CASCADE)
    nutriscore = models.CharField(max_length=1)
    energy_100g = models.DecimalField(max_digits=7, decimal_places=2)
    energy_unit = models.CharField(max_length=5)
    proteins_100g = models.DecimalField(max_digits=6, decimal_places=2)
    fat_100g = models.DecimalField(max_digits=6, decimal_places=2)
    saturated_fat_100g = models.DecimalField(max_digits=6, decimal_places=2)
    carbohydrates_100g = models.DecimalField(max_digits=6, decimal_places=2)
    sugars_100g = models.DecimalField(max_digits=6, decimal_places=2)
    fiber_100g = models.DecimalField(max_digits=6, decimal_places=2)
    salt_100g = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return "Objet nutrition lié à {}".format(self.product.product_name)

    class Meta:
        db_table = "nutrition"

class Media(models.Model):
    product = models.OneToOneField(Product, to_field="product_name", primary_key=True, on_delete=models.CASCADE)
    image_full_url = models.TextField() 
    image_front_url = models.TextField() 

    class Meta:
        db_table = "media"

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    mail_address = models.CharField(max_length=200)
    password = models.CharField(max_length=48)

    class Meta:
        db_table = "user"

class Record(models.Model):
    record_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, to_field="user_id", on_delete=models.CASCADE)
    product_recorded = models.ForeignKey(Product, to_field="product_name", on_delete=models.CASCADE, related_name='product_recorded_set')
    product_searched = models.ForeignKey(Product, to_field="product_name", on_delete=models.CASCADE, related_name='product_searched_set')

    class Meta:
        db_table = "record"