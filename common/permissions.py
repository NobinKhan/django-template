from rest_framework.permissions import BasePermission


# User Permissions
class AddUser(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to create new user!"

    def has_permission(self, request, view):
        return request.user.has_perm('users.add_user')


class ChangeUser(BasePermission):
    """Allow access to change user only"""

    message = "You don't have permission to edit user!"

    def has_permission(self, request, view):
        return request.user.has_perm('users.change_user')
      
class ViewUser(BasePermission):
    """Allow access to view user only"""

    message = "You don't have permission to view user!"

    def has_permission(self, request, view):
        return request.user.has_perm('users.view_user')


class DeleteUser(BasePermission):
    """Allow access to delete user only"""

    message = "You don't have permission to view user!"

    def has_permission(self, request, view):
        return request.user.has_perm('users.delete_user')


class ViewRole(BasePermission):
    """Allow access to view role only"""

    message = "You don't have permission to view roles!"

    def has_permission(self, request, view):
        return request.user.has_perm('auth.view_group')


# Product Permissions

class AddSubNumber(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to create new sub_number!"

    def has_permission(self, request, view):
        return request.user.has_perm('product.add_subnumber')


class AddUploadProduct(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to create new Product!"

    def has_permission(self, request, view):
        return request.user.has_perm('product.add_uploadproduct')


class DeleteUploadProduct(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to remove existing Product!"

    def has_permission(self, request, view):
        return request.user.has_perm('product.delete_uploadproduct')


class ViewUploadProduct(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to view Products!"

    def has_permission(self, request, view):
        return request.user.has_perm('product.view_uploadproduct')


class ChangeUploadProduct(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to change Products!"

    def has_permission(self, request, view):
        return request.user.has_perm('product.change_uploadproduct')


class ViewProduct(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to view Products!"

    def has_permission(self, request, view):
        return request.user.has_perm('product.view_product')


class AddProduct(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to scan Products!"

    def has_permission(self, request, view):
        return request.user.has_perm('product.add_product')


# Emails permissions
class AddEmail(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to add new email!"

    def has_permission(self, request, view):
        return request.user.has_perm('emails.add_email')


class ViewEmail(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to view email!"

    def has_permission(self, request, view):
        return request.user.has_perm('emails.view_email')


class ChangeEmail(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to edit email!"

    def has_permission(self, request, view):
        return request.user.has_perm('emails.change_email')


class DeleteEmail(BasePermission):
    """Allow access to create user only"""

    message = "You don't have permission to delete email!"

    def has_permission(self, request, view):
        return request.user.has_perm('emails.delete_email')

class AdminUser(BasePermission):
    message = "You donot have all permission"
    
    def has_permission(self, request, view):
        
        return request.user.get_all_permissions()