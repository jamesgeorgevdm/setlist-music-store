"""
Defines user roles/groups and assigns Django model-level permissions
for buyers and composers in the SetList platform.
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from set_list.models import SheetMusic, Collection, Review, Purchase, Composer

def setup_groups():
    """
    Creates 'buyer' and 'composer' user groups and assigns relevant permissions
    to each based on their expected roles in the system.

    - Composers can add, edit, delete, and view collections and sheet music.
    - Buyers can purchase sheet music, view collections, and leave reviews.
    """

    # Create or get the Buyer and Composer groups
    buyer_group, _ = Group.objects.get_or_create(name="buyer")
    composer_group, _ = Group.objects.get_or_create(name="composer")

    # Permissions for Composer group
    composer_permissions = [
        ("add_collection", Collection),
        ("change_collection", Collection),
        ("delete_collection", Collection),
        ("view_collection", Collection),
        ("view_review", Review),
        ("add_sheetmusic", SheetMusic),
        ("change_sheetmusic", SheetMusic),
        ("delete_sheetmusic", SheetMusic),
        ("view_sheetmusic", SheetMusic),
    ]

    # Permissions for Buyer group
    buyer_permissions = [
        ("view_collection", Collection),
        ("view_composer", Composer),
        ("add_purchase", Purchase),
        ("change_purchase", Purchase),
        ("delete_purchase", Purchase),
        ("view_purchase", Purchase),
        ("add_review", Review),
        ("change_review", Review),
        ("delete_review", Review),
        ("view_review", Review),
        ("view_sheetmusic", SheetMusic),
    ]

    def assign_permissions(group, permissions):
        """
        Helper function that assigns a list of permissions to a group.
        :param group: The Django Group instance.
        :param permissions: A list of (codename, model) tuples.
        """
        for codename, model in permissions:
            content_type = ContentType.objects.get_for_model(model)
            permission = Permission.objects.get(
                codename=codename, content_type=content_type
            )
            group.permissions.add(permission)

    # Apply permissions
    assign_permissions(composer_group, composer_permissions)
    assign_permissions(buyer_group, buyer_permissions)

    print("Buyer and Composer groups set up with appropriate permissions.")
