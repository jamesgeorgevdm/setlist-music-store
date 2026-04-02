"""
views.py

Contains the primary view logic for the SetList application, including:
- User authentication (login/registration/logout)
- Collection CRUD operations
- Sheet music addition to collections
- Username/email/password validators
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, send_mail
from datetime import datetime, timedelta
from hashlib import sha1
import secrets

from .twitter_auth import post_tweet
from .models import Composer, SheetMusic, Collection, ResetToken, Review, Purchase
from .forms import SheetMusicForm, CollectionForm, ReviewForm


def auth_view(request):
    """
    Handles both login and registration from a single view.

    POST:
        - Registers new users if 'register' is in request.POST.
        - Logs users in if 'login' is in request.POST.

    GET:
        - Renders the authentication form.
    """
    if request.method == "POST":
        if "register" in request.POST:
            username = request.POST["username"]
            password = request.POST["password"]
            email = request.POST["email"]
            user_type = request.POST.get("user_type")

            is_valid_username, username_msg = verify_username(username)
            is_valid_password, password_msg = verify_password(password)
            is_valid_email, email_msg = verify_email(email)

            if is_valid_username and is_valid_password and is_valid_email:
                user = User.objects.create_user(
                    username=username, password=password, email=email
                )

                if user_type in ["composer", "buyer"]:
                    try:
                        group = Group.objects.get(name=user_type)
                        user.groups.add(group)
                    except Group.DoesNotExist:
                        return render(
                            request,
                            "auth.html",
                            {"error": f"Group {user_type} does not exist."},
                        )

                user.save()
                login(request, user)

                request.session.set_expiry(0)  # Expires on browser close
                request.session["user_id"] = user.id
                request.session["user_type"] = user_type

                return redirect("collection_list")
            else:
                error_message = (
                    username_msg if not is_valid_username else
                    password_msg if not is_valid_password else
                    email_msg
                )
                return render(request, "auth.html", {"error": error_message})

        elif "login" in request.POST:
            username = request.POST["login_username"]
            password = request.POST["login_password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                request.session["user_id"] = user.id

                if user.groups.filter(name="composer").exists():
                    request.session["user_type"] = "composer"
                elif user.groups.filter(name="buyer").exists():
                    request.session["user_type"] = "buyer"

                return redirect("collection_list")
            else:
                return render(request, "auth.html", {"error": "Invalid credentials"})

    return render(request, "auth.html")


def logout_user(request):
    """
    Logs out the current user and clears the session.
    """
    logout(request)
    return redirect("auth")


def verify_username(username):
    """
    Validates a username for length, uniqueness, and formatting.
    """
    if len(username) < 5:
        return False, "Username must be at least 5 characters long."
    if len(username) > 20:
        return False, "Username must be at most 20 characters long."
    if User.objects.filter(username=username).exists():
        return False, "Username already exists."
    return True, None


def verify_email(email):
    """
    Validates an email address for format and uniqueness.
    """
    if len(email) < 6:
        return False, "Email must be at least 6 characters long."
    if not any(char in "@." for char in email):
        return False, "Email must be in the valid format."
    if User.objects.filter(email=email).exists():
        return False, "That email address is already associated with an account."
    return True, None


def verify_password(password):
    """
    Validates password strength.
    Checks for length, digits, letters, uppercase, and special characters.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if len(password) > 30:
        return False, "Password cannot be more than 30 characters long."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."
    if not any(char.isalpha() for char in password):
        return False, "Password must contain at least one letter."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(char in "!@#$%^&*()-_+=<>?{}[]|:;\"'`~" for char in password):
        return False, "Password must contain at least one special character."
    return True, None


# ---------- Collection Views ----------


@login_required
def collection_list(request):
    collections = Collection.objects.all()
    form = None

    if request.user.is_authenticated:
        if request.method == "POST":
            form = CollectionForm(request.POST, request.FILES)
            if form.is_valid():
                new_collection = form.save(commit=False)
                new_collection.composer = request.user
                new_collection.save()
                try:
                    message = f"New music collection available: {new_collection.name}!"
                    post_tweet(message)
                except Exception as e:
                    # Logs to Render console, but allows the redirect to happen
                    print(f"Twitter Auto-Post Failed: {e}")
                    messages.warning(request, "Collection created, but Twitter is currently unavailable.")
                
                return redirect("collection_list")
        else:
            form = CollectionForm()

    return render(
        request,
        "collection_list.html",
        {"collections": collections, "form": form},
    )


@login_required
def collection_detail(request, pk):
    """
    Displays the details of a specific collection.
    Allows the composer to add new sheet music to it.
    """
    collection = get_object_or_404(Collection, pk=pk)
    sheet_music_list = SheetMusic.objects.filter(collection=collection)

    # Annotate edit permissions for template logic
    for sheet_music in sheet_music_list:
        sheet_music.can_edit = sheet_music.composer == request.user

    can_add_music = collection.composer == request.user
    form = None

    if can_add_music:
        if request.method == "POST":
            form = SheetMusicForm(request.POST, request.FILES)
            if form.is_valid():
                new_music = form.save(commit=False)
                new_music.collection = collection
                new_music.composer = collection.composer
                new_music.save()
                messages.success(request, "Sheet music added successfully.")
                return redirect("collection_detail", pk=collection.pk)
        else:
            form = SheetMusicForm()

    context = {
        "collection": collection,
        "sheet_music_list": sheet_music_list,
        "form": form,
        "can_add_music": can_add_music,
    }
    return render(request, "collection_detail.html", context)


@login_required
def collection_edit(request, pk):
    """
    Allows the original composer to edit an existing collection.
    """
    collection = get_object_or_404(Collection, pk=pk)

    if collection.composer != request.user:
        return redirect("collection_list")

    form = CollectionForm(instance=collection)
    if request.method == "POST":
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            form.save()
            return redirect("collection_list")

    return render(
        request, "collection_edit.html", {"collection": collection, "form": form}
    )


@login_required
def collection_delete(request, pk):
    """
    Allows the original composer to delete a collection.
    """
    collection = get_object_or_404(Collection, pk=pk)

    if collection.composer != request.user:
        return redirect("collection_list")

    if request.method == "POST":
        collection.delete()
        return redirect("collection_list")

    return redirect("collection_list")


# Music functionality and views


@login_required(login_url="auth")
def music_list(request):
    """View to display all sheet music."""
    # Only users with view permission can access this page.
    if request.user.has_perm("set_list.view_sheetmusic"):
        sheet_music = SheetMusic.objects.all()
        context = {
            "sheet_music": sheet_music,
        }
        return render(request, "music_list.html", context)
    else:
        return HttpResponseForbidden("You do not have permission to view this page.")


@login_required(login_url="auth")
def music_detail(request, pk):
    """View to display details of a specific post and handle reviews."""
    # Check if the user has permission to view sheet music
    if not request.user.has_perm("set_list.view_sheetmusic"):
        return redirect("collection_list")  # or a 403 page

    sheet_music = get_object_or_404(SheetMusic, pk=pk)
    reviews = Review.objects.filter(sheet_music=sheet_music).order_by("-created_at")

    is_composer = sheet_music.composer == request.user
    has_reviewed = Review.objects.filter(
        sheet_music=sheet_music, user=request.user
    ).exists()
    form = None

    # Only non-composers can review, and only once
    if not is_composer and not has_reviewed:
        form = ReviewForm(request.POST or None)
        if request.method == "POST" and form.is_valid():
            review = form.save(commit=False)
            review.sheet_music = sheet_music
            review.user = request.user
            review.verified = Purchase.objects.filter(
                user=request.user, sheet_music=sheet_music
            ).exists()
            review.save()
            return redirect("music_detail", pk=pk)

    return render(
        request,
        "music_detail.html",
        {
            "sheet_music": sheet_music,
            "reviews": reviews,
            "form": form,
            "is_composer": is_composer,
            "has_reviewed": has_reviewed,
        },
    )


@login_required(login_url="auth")
def music_create(request):
    """View to create new sheet music."""
    if request.user.has_perm("set_list.add_sheetmusic"):
        form = SheetMusicForm(request.POST or None, request.FILES or None)

        # Restrict collection queryset to only the collections belonging to the user
        form.fields["collection"].queryset = Collection.objects.filter(
            composer=request.user
        )

        if request.method == "POST" and form.is_valid():
            sheetmusic = form.save(commit=False)
            sheetmusic.composer = (
                request.user
            )  # Override composer field to ensure it's the current user
            sheetmusic.save()
            return redirect("music_list")

        return render(request, "music_form.html", {"form": form})
    else:
        return HttpResponseForbidden("You do not have permission to create new music.")


@login_required(login_url="auth")
def music_update(request, pk):
    """View to update existing sheet music."""
    sheet_music = get_object_or_404(SheetMusic, pk=pk)
    if request.user != sheet_music.composer:
        return HttpResponseForbidden("You do not have permission to edit this music.")

    # Restrict collection queryset to only the collections belonging to the user
    form = SheetMusicForm(
        request.POST or None, request.FILES or None, instance=sheet_music
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("music_detail", pk=sheet_music.pk)

    return render(request, "music_form.html", {"form": form})


@login_required(login_url="auth")
def music_delete(request, pk):
    """View to delete existing sheet music."""
    sheet_music = get_object_or_404(SheetMusic, pk=pk)

    if request.user != sheet_music.composer:
        return HttpResponseForbidden("You do not have permission to delete this music.")

    # Deletes immediately and redirects to collection detail
    collection_pk = sheet_music.collection.pk
    sheet_music.delete()
    return redirect("collection_detail", pk=collection_pk)


# Cart functionality and views


@login_required(login_url="auth")
def add_item_to_cart(request, product_id):
    """Add an item to the user's cart."""
    quantity = int(request.POST.get("quantity", 1))
    cart = request.session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + quantity
    request.session["cart"] = cart
    return redirect("show_user_cart")


@login_required(login_url="auth")
def update_cart_item(request, product_id):
    """Update the quantity of an item in the user's cart."""
    if request.method == "POST":
        quantity = int(
            request.POST.get("quantity", 1)
        )  # Get the quantity from the form
        cart = request.session.get("cart", {})
        if quantity > 0:
            cart[str(product_id)] = quantity
        else:
            cart.pop(str(product_id), None)
        request.session["cart"] = cart
    return redirect("show_user_cart")


@login_required(login_url="auth")
def remove_cart_item(request, product_id):
    """Remove an item from the user's cart."""
    cart = request.session.get("cart", {})  # Request current session cart
    cart.pop(str(product_id), None)  # Remove the item if it exists
    request.session["cart"] = cart
    return redirect("show_user_cart")


@login_required(login_url="auth")
def show_user_cart(request):
    """Display the user's cart."""
    cart = request.session.get("cart", {})
    items = []
    total = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(SheetMusic, id=product_id)
        item_total = product.price * quantity
        items.append(
            {
                "product": product,
                "quantity": quantity,
                "total": item_total,
            }
        )
        total += item_total
    return render(request, "cart.html", {"items": items, "total": total})


@login_required(login_url="auth")
def checkout(request):
    """Handle the checkout process and email service for the user's cart."""
    # Only allow buyers (non-composers) to checkout
    if hasattr(request.user, "composer"):
        messages.error(request, "Composers cannot purchase sheet music.")
        return render(request, "cart.html", {"message": "Composers cannot checkout."})

    cart = request.session.get("cart", {})
    if not cart:
        return render(request, "cart.html", {"message": "Your cart is empty."})

    items = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(SheetMusic, id=product_id)
        item_total = product.price * quantity

        items.append({"product": product, "quantity": quantity, "total": item_total})

        total += item_total

        # Record the purchase (for verification of reviews)
        for _ in range(quantity):
            Purchase.objects.create(user=request.user, sheet_music=product)

    # Render invoice HTML
    invoice_html = render_to_string(
        "invoice_email.html",
        {
            "user": request.user,
            "items": items,
            "total": total,
        },
    )
    # Send invoice email with safety net
    try:
        send_mail(
            subject="Your Sheet Music Invoice",
            message="Your invoice is attached.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            html_message=invoice_html,
        )
    except Exception as e:
        print(f"Email Delivery Failed: {e}")
        messages.error(request, "Purchase confirmed, but we couldn't email your invoice. Please contact support.")

    # Clear the cart even if email fails
    request.session["cart"] = {}

    return render(request, "cart.html", {"message": "Success! (Note: Check 'Messages' for email status)"})


# Forgot Password Section


def build_email(user, reset_url):
    """Builds the email for password reset."""
    subject = "Password Reset"
    user_email = user.email
    domain_email = "example@domain.com"
    body = f"Hi {user.username},\nHere is your link to reset your password: {reset_url}"
    email = EmailMessage(subject, body, domain_email, [user_email])
    return email


def generate_reset_url(user):
    """Generates a password reset URL for the user."""
    domain = "http://127.0.0.1:8000"
    token = secrets.token_urlsafe(16)
    expiry_date = datetime.now() + timedelta(minutes=5)

    # Save hashed token to DB
    ResetToken.objects.create(
        user=user, token=sha1(token.encode()).hexdigest(), expiry_date=expiry_date
    )

    reset_path = reverse("password_reset", kwargs={"token": token})
    return f"{domain}{reset_path}"


def send_password_reset(request):
    try:
        user_email = request.POST.get("email")
        user = User.objects.get(email=user_email)
        url = generate_reset_url(user)
        email = build_email(user, url)
        email.send()
        messages.success(request, "Reset link sent! Please check your inbox.")
    except User.DoesNotExist:
        messages.error(request, "No account found with that email.")
    except Exception as e:
        print(f"Password Reset Email Failed: {e}")
        messages.error(request, "We encountered an error sending the email. Please try again later.")
    
    return HttpResponseRedirect(reverse("auth"))

def reset_user_password(request, token):
    """Handles the password reset process."""
    hashed_token = sha1(token.encode()).hexdigest()

    # Check if the token exists and is not expired
    try:
        user_token = ResetToken.objects.get(token=hashed_token)
        if user_token.expiry_date.replace(tzinfo=None) < datetime.now():
            user_token.delete()
            return render(request, "password_reset.html", {"token": None})
    except ResetToken.DoesNotExist:
        return render(request, "password_reset.html", {"token": None})

    # If the token is valid, allow the user to reset their password
    if request.method == "POST":
        password = request.POST.get("password")
        password_conf = request.POST.get("password_conf")

        if password == password_conf:
            user = user_token.user
            user.set_password(password)
            user.save()
            user_token.delete()
            return redirect("auth")
        else:
            return render(
                request,
                "password_reset.html",
                {"token": user_token, "error": "Passwords do not match."},
            )

    return render(request, "password_reset.html", {"token": user_token})


def reset_password_request(request):
    """
    Renders the password reset request page and triggers email on POST.

    This view:
    - Accepts user email input via form
    - Sends a reset link to the user if the email exists
    """
    if request.method == "POST":
        return send_password_reset(request)
    return render(request, "reset_password_request.html")


def change_user_password(username, new_password):
    """
    Manually resets the password for a specific user (admin/system use only).

    Args:
        username (str): The user's username.
        new_password (str): The new password to assign.
    """
    User = get_user_model()
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()
