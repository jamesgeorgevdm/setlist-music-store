from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Composer(models.Model):
    """
    Represents a music composer with optional website and biography.
    This model may be used for displaying public composer information.
    """
    name = models.CharField(max_length=100, help_text="Full name of the composer.")
    bio = models.TextField(help_text="Short biography of the composer.")
    website = models.URLField(blank=True, null=True, help_text="Optional website URL.")

    def __str__(self):
        return self.name


class Collection(models.Model):
    """
    Represents a themed or curated group of SheetMusic items,
    tied to a specific composer (User in the 'composer' group).
    """
    composer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="collections",
        help_text="The composer (User) who created this collection."
    )
    title = models.CharField(max_length=200, help_text="Title of the collection.")
    description = models.TextField(blank=True, help_text="Optional description.")
    image = models.ImageField(
        upload_to="images/collections/",
        null=True,
        blank=True,
        help_text="Optional image for the collection."
    )

    def __str__(self):
        return f"{self.title} (by {self.composer.username})"


class SheetMusic(models.Model):
    """
    Represents a single piece of sheet music. Includes pricing, an optional image,
    and associations to a composer and optional collection.
    """
    composer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"groups__name": "composer"},
        help_text="User who composed this music. Must belong to 'composer' group."
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="sheetmusic",
        help_text="Optional collection that this piece belongs to."
    )
    title = models.CharField(max_length=255, help_text="Title of the sheet music.")
    genre = models.CharField(max_length=100, help_text="Genre of the composition.")
    description = models.TextField(help_text="Detailed description or program notes.")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price in currency units (e.g., 9.99)."
    )
    image = models.ImageField(
        upload_to="images/",
        null=True,
        blank=True,
        help_text="Optional cover image or preview of the music."
    )

    def __str__(self):
        return self.title


class Purchase(models.Model):
    """
    Represents a transaction where a user has purchased a specific SheetMusic item.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who made the purchase."
    )
    sheet_music = models.ForeignKey(
        SheetMusic,
        on_delete=models.CASCADE,
        help_text="The purchased sheet music item."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of purchase."
    )

    def __str__(self):
        return f"{self.user.username} bought {self.sheet_music.title}"


class Review(models.Model):
    """
    Represents a user's review for a SheetMusic item. Ratings are from 1 to 5 stars.
    """
    sheet_music = models.ForeignKey(
        SheetMusic,
        on_delete=models.CASCADE,
        help_text="The sheet music being reviewed."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who wrote the review."
    )
    rating = models.PositiveIntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        help_text="Rating from 1 (lowest) to 5 (highest)."
    )
    comment = models.TextField(help_text="Written feedback.")
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Time the review was submitted."
    )
    verified = models.BooleanField(
        default=False,
        help_text="Flag to indicate if the review has been verified."
    )

    def __str__(self):
        return f"Review by {self.user.username} on {self.sheet_music.title}"


class ResetToken(models.Model):
    """
    Represents a password reset or account recovery token.
    Stores an expiry time and a flag indicating if it's already used.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="User who requested the token."
    )
    token = models.CharField(max_length=500, help_text="Secure token string.")
    expiry_date = models.DateTimeField(help_text="When the token expires.")
    used = models.BooleanField(default=False, help_text="Whether the token has been used.")

    def __str__(self):
        return f"Reset token for {self.user.username} (used={self.used})"
