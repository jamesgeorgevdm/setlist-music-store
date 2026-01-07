from django import forms
from django.contrib.auth.models import User
from .models import SheetMusic, Collection, Review

class SheetMusicForm(forms.ModelForm):
    """
    A form for creating or updating SheetMusic entries.
    The composer field is limited to users in the 'composer' group.
    """
    composer = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="composer"),
        label="Composer Username",
    )

    class Meta:
        model = SheetMusic
        fields = ["composer", "collection", "title", "genre", "description", "price", "image"]


class CollectionForm(forms.ModelForm):
    """
    A form for creating or editing music Collections.
    Includes only the title and description fields.
    """
    class Meta:
        model = Collection
        fields = ["title", "description", "image"]


class ReviewForm(forms.ModelForm):
    """
    A form for submitting a Review of a sheet music piece.
    Only includes the rating and comment fields.
    """
    class Meta:
        model = Review
        fields = ["rating", "comment"]
