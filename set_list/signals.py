"""
Signal handlers for the SetList app.

Includes:
- Automatic Twitter posting when new collections or sheet music are created.
- Group permission setup triggered post-migration.
"""

import os
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from .models import Collection, SheetMusic
from .twitter_auth import TwitterAuthClient
from .setup_groups import setup_groups


@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    """
    Ensures user groups and permissions are initialized after database migration.
    """
    if sender.name == "set_list":
        setup_groups()


# Initialize Twitter session once per app load
twitter = TwitterAuthClient()
twitter.restore_session()


@receiver(post_save, sender=Collection)
def tweet_collection_created(sender, instance, created, **kwargs):
    """
    Posts a tweet when a new collection is created.
    Includes optional image if available.
    """
    if created:
        composer_name = instance.composer.username
        tweet = f"A New Collection by {composer_name} has been added!\n\n{instance.title}\n{instance.description}"
        image = (
            instance.image.path
            if instance.image and os.path.isfile(instance.image.path)
            else None
        )
        twitter.post_tweet(tweet, media_path=image)


@receiver(post_save, sender=SheetMusic)
def tweet_sheetmusic_created(sender, instance, created, **kwargs):
    """
    Posts a tweet when a new sheet music product is created.
    Mentions composer, collection, and details.
    """
    if created:
        tweet = (
            f"New Product from {instance.composer.username} featured in {instance.collection.title}!\n\n"
            f"Title: {instance.title}\n"
            f"Genre: {instance.genre}\n"
            f"Description: {instance.description}\n"
            f"Price: R{instance.price:.2f}"
        )
        image = (
            instance.image.path
            if instance.image and os.path.isfile(instance.image.path)
            else None
        )
        twitter.post_tweet(tweet, media_path=image)
