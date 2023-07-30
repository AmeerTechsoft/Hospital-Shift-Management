from django.contrib.auth.backends import ModelBackend
from django.urls import reverse


class RegularUserRedirectBackend(ModelBackend):
    def get_user_permissions(self, user_obj, obj=None):
        if user_obj.is_superuser:
            return []
        return super().get_user_permissions(user_obj, obj=obj)

    def get_group_permissions(self, user_obj, obj=None):
        if user_obj.is_superuser:
            return set()
        return super().get_group_permissions(user_obj, obj=obj)

    def get_all_permissions(self, user_obj, obj=None):
        if user_obj.is_superuser:
            return set()
        return super().get_all_permissions(user_obj, obj=obj)

    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_superuser:
            return False
        return super().has_perm(user_obj, perm, obj=obj)

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user and not user.is_superuser:
            return user
        return None

    def get_redirect_url(self, request):
        return reverse('dashboard')
