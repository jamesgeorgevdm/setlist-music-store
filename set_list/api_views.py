"""
API views for the SetList eCommerce application.

Defines endpoints for retrieving and creating collections (stores),
sheet music (products), and viewing related reviews.
Includes appropriate permission handling and user-bound filtering.
"""

from rest_framework import generics, permissions
from .models import Collection, SheetMusic, Review
from .serializers import CollectionSerializer, SheetMusicSerializer, ReviewSerializer
from .permissions import IsComposerOrReadOnly


class MyCollectionsAPI(generics.ListAPIView):
    """
    Returns a list of collections belonging to the currently authenticated composer.
    Access restricted to logged-in users.
    """
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Collection.objects.filter(composer=self.request.user)


class CollectionListCreateAPI(generics.ListCreateAPIView):
    """
    GET: Returns all collections.
    POST: Allows authenticated composers to create a new collection.
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsComposerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(composer=self.request.user)


class CollectionDetailAPI(generics.RetrieveAPIView):
    """
    Returns detailed data for a specific collection by ID.
    Publicly accessible.
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.AllowAny]


class ComposerCollectionsAPI(generics.ListAPIView):
    """
    Returns all collections created by a specific composer (vendor), via composer_id.
    Publicly accessible.
    """
    serializer_class = CollectionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Collection.objects.filter(composer_id=self.kwargs.get('composer_id'))


class SheetMusicListCreateAPI(generics.ListCreateAPIView):
    """
    GET: Returns all sheet music across the platform.
    POST: Allows authenticated composers to upload new sheet music.
    """
    queryset = SheetMusic.objects.all()
    serializer_class = SheetMusicSerializer
    permission_classes = [IsComposerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(composer=self.request.user)


class ReviewListAPI(generics.ListAPIView):
    """
    Returns a list of all reviews associated with a given sheet music item.
    Filtered using sheet_music_id.
    Publicly accessible.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        sheet_music_id = self.kwargs.get('sheet_music_id')
        return Review.objects.filter(sheet_music__id=sheet_music_id)
