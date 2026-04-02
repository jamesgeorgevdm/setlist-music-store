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

# Initialize Twitter session safely
twitter = TwitterAuthClient()
try:
    twitter.restore_session()
except Exception as e:
    print(f"Twitter Initialization Warning: {e}")

@receiver(post_save, sender=Collection)
def tweet_collection_created(sender, instance, created, **kwargs):
    """
    Posts a tweet when a new collection is created.
    Wrapped in try-except to prevent 503/API errors from crashing the app.
    """
    if created:
        try:
            composer_name = instance.composer.username
            tweet = f"A New Collection by {composer_name} has been added!\n\n{instance.title}\n{instance.description}"
            
            image = None
            if instance.image:
                try:
                    if os.path.isfile(instance.image.path):
                        image = instance.image.path
                except (ValueError, RuntimeError):
                    image = None

            twitter.post_tweet(tweet, media_path=image)
        except Exception as e:
            print(f"Twitter Collection Signal Error: {e}")

@receiver(post_save, sender=SheetMusic)
def tweet_sheetmusic_created(sender, instance, created, **kwargs):
    """
    Posts a tweet when a new sheet music product is created.
    Wrapped in try-except to prevent 503/API errors from crashing the app.
    """
    if created:
        try:
            tweet = (
                f"New Product from {instance.composer.username} featured in {instance.collection.title}!\n\n"
                f"Title: {instance.title}\n"
                f"Genre: {instance.genre}\n"
                f"Description: {instance.description}\n"
                f"Price: R{instance.price:.2f}"
            )
            
            image = None
            if instance.image:
                try:
                    if os.path.isfile(instance.image.path):
                        image = instance.image.path
                except (ValueError, RuntimeError):
                    image = None

            twitter.post_tweet(tweet, media_path=image)
        except Exception as e:
            print(f"Twitter SheetMusic Signal Error: {e}")