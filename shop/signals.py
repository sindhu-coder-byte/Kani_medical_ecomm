from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def create_default_categories(sender, **kwargs):
    if sender.name == 'shop':  # only run for our shop app
        Category = apps.get_model('shop', 'Category')
        default_categories = [
            "All Products",
            "Baby Care",
            "Health Devices",
            "Personal Care",
            "Skin Care",
            "Ayurvedic"
        ]
        for cat_name in default_categories:
            Category.objects.get_or_create(name=cat_name)
