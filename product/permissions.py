from rest_framework import permissions
from .models import Vendor  # Import your Vendor model

class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if request.user and request.user.is_authenticated:
            # Check if the user is associated with a Vendor model
            try:
                vendor = Vendor.objects.get(user=request.user)
                return True  # The user is associated with a Vendor model
            except Vendor.DoesNotExist:
                return False  # The user is not associated with a Vendor model
        return False  # User is not authenticated

