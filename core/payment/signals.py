from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ShippingAddress

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_shipping_address(sender, instance, created, **kwargs):
    """
    Create a default shipping address for a newly created user.

    This function is a signal receiver that is triggered after a User object is saved.
    If the User object is newly created, it checks if a ShippingAddress object already exists for the user.
    If not, it creates a default shipping address using
    the ShippingAddress.create_default_shipping_address method.

    Parameters:
        sender (class): The class of the sender model.
        instance (User): The User instance that was saved.
        created (bool): A boolean indicating if the User instance was created.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if created:
        if not ShippingAddress.objects.filter(user=instance).exists():
            ShippingAddress.create_default_shipping_address(user=instance)
