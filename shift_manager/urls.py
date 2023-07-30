from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .views import DashboardView

urlpatterns = [
    # path('dashboard/', login_required(DashboardView.as_view()), name='dashboard'),
    # path('shift_manager/dashboard', login_required(UserProfileView.as_view()), name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('submit_complaint/', views.submit_complaint, name='submit_complaint'),
    path('change_password/', views.change_password, name='change_password'),
    path('manage-departments/', views.manage_departments, name='manage_departments'),
    path('', auth_views.LoginView.as_view(template_name='shift_manager/login.html'), name='login'),
    path('clock-in-out/', views.clock_in_out, name='clock-in'),
    path('signout', views.signout, name='signout'),


]
