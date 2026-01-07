"""
Unit tests for the SheetMusic API endpoints.

Covers:
- Creation failure when no collection is provided.
- Successful creation with valid collection and composer.
"""

import uuid

from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from set_list.models import Collection
from set_list.signals import tweet_collection_created


class SheetMusicCreationTests(APITestCase):
    """
    Test suite for validating SheetMusic creation via API.
    Ensures collection field is required and composer logic works.
    """

    def setUp(self):
        """
        Sets up an authenticated composer user, a test collection,
        and disables tweet signals during collection creation to avoid duplicate tweet errors.
        """
        post_save.disconnect(tweet_collection_created, sender=Collection)

        self.composer_group, _ = Group.objects.get_or_create(name="composer")
        self.composer = User.objects.create_user(
            username="testcomposer", password="strongpass123"
        )
        self.composer.groups.add(self.composer_group)

        self.token = Token.objects.create(user=self.composer)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.collection = Collection.objects.create(
            composer=self.composer,
            title=f"Test Collection {uuid.uuid4().hex[:6]}",
            description="A test collection for unit testing."
        )

        post_save.connect(tweet_collection_created, sender=Collection)

    def test_sheetmusic_requires_collection(self):
        """
        Ensure the API returns 400 Bad Request when trying to create
        SheetMusic without specifying a collection.
        """
        data = {
            "title": "Floating Waltz",
            "genre": "Contemporary",
            "description": "A tranquil solo work.",
            "price": "12.99"
        }
        response = self.client.post("/api/sheetmusic/", data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("collection", response.data)

    def test_sheetmusic_with_valid_collection_creates_successfully(self):
        """
        Test that SheetMusic can be created when all required fields,
        including a valid collection and composer, are provided.
        """
        data = {
            "title": "Aurora Skies",
            "genre": "Neo-Romantic",
            "description": "Evokes the feeling of dancing light.",
            "price": "18.00",
            "collection": self.collection.id,
            "composer": self.composer.id
        }
        response = self.client.post("/api/sheetmusic/", data, format="json")
        print("Status code:", response.status_code)
        print("Response data:", response.data)
        self.assertEqual(response.status_code, 201)
