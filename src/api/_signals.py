from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Generation


@receiver(post_save, sender=Message)
def add_generation_to_message(sender, instance, created, **kwargs):
    if created:
        # Create a new Generation instance
        generation = Generation.objects.create(
            name=f"Generation for message {instance.id}"
        )
        # Associate the Generation instance with the Message instance
        instance.generation = generation
        instance.save()
