"""
Serializers for converting model instances into JSON for API responses.
"""

from rest_framework import serializers
from .models import Composer, Collection, SheetMusic, Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    """

    class Meta:
        model = Review
        fields = '__all__'


class SheetMusicSerializer(serializers.ModelSerializer):
    """
    Serializer for SheetMusic model.
    Includes nested list of related reviews (read-only).
    """
    reviews = ReviewSerializer(many=True, read_only=True, source='review_set')

    class Meta:
        model = SheetMusic
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer for Collection model.
    Includes nested sheet music items (read-only).
    """
    sheetmusic = SheetMusicSerializer(many=True, read_only=True, source='sheetmusic')

    class Meta:
        model = Collection
        fields = '__all__'
