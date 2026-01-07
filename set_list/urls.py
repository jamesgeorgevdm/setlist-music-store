"""
URL configuration for the SetList Django project.

Routes:
- Web views (auth, cart, collections, music, checkout)
- Password reset endpoints
- REST API endpoints (secured and public)
- Static/media handling for development
"""

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token
from . import api_views
from .views import (
    auth_view,
    music_list,
    music_detail,
    music_create,
    music_update,
    music_delete,
    show_user_cart,
    add_item_to_cart,
    update_cart_item,
    remove_cart_item,
    checkout,
    reset_user_password,
    reset_password_request,
    collection_list,
    collection_detail,
    collection_edit,
    collection_delete,
)

urlpatterns = [
    # --- Web Application Views ---
    path("", auth_view, name="auth"),
    path("collections/", collection_list, name="collection_list"),
    path("collections/<int:pk>/", collection_detail, name="collection_detail"),
    path("collections/<int:pk>/edit/", collection_edit, name="collection_edit"),
    path("collections/<int:pk>/delete/", collection_delete, name="collection_delete"),

    path("list/", music_list, name="music_list"),
    path("detail/<int:pk>/", music_detail, name="music_detail"),
    path("create/", music_create, name="music_create"),
    path("update/<int:pk>/", music_update, name="music_update"),
    path("delete/<int:pk>/", music_delete, name="music_delete"),

    path("cart/", show_user_cart, name="show_user_cart"),
    path("cart/add/<int:product_id>/", add_item_to_cart, name="add_item_to_cart"),
    path("cart/update/<int:product_id>/", update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:product_id>/", remove_cart_item, name="remove_cart_item"),
    path("checkout/", checkout, name="checkout"),
    path("reset_password_request/", reset_password_request, name="reset_request"),
    path("reset_password/<str:token>/", reset_user_password, name="password_reset"),
    path("logout/", auth_view, name="logout"),

    # --- API Endpoints ---
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path("api/my-collections/", api_views.MyCollectionsAPI.as_view(), name="api_my_collections"),
    path("api/composers/<int:composer_id>/collections/", api_views.ComposerCollectionsAPI.as_view(), name="composer_collections"),
    path("api/collections/", api_views.CollectionListCreateAPI.as_view(), name="api_collection_list_create"),
    path("api/collections/<int:pk>/detail/", api_views.CollectionDetailAPI.as_view(), name="api_collection_detail"),
    path("api/sheetmusic/", api_views.SheetMusicListCreateAPI.as_view(), name="api_sheetmusic_list_create"),
    path("api/sheetmusic/<int:sheet_music_id>/reviews/", api_views.ReviewListAPI.as_view(), name="api_review_list"),
]

# Serve uploaded media in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
