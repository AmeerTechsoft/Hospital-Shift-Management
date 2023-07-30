import datetime
import random
from collections import defaultdict
from functools import wraps

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.forms import formset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.utils.datetime_safe import date
from django.utils.timezone import now

from .forms import ShiftForm
from .models import Department, Category, Employee, Shift, Clock, Complaint
from django.views.generic import TemplateView

# Create your views here.


def login(request):
    if request.method == 'POST':
        user_id = request.POST['user_id']
        password = request.POST['password']
        user = authenticate(request, username=user_id, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', None)
            if next_url is not None:
                return redirect(next_url)
            else:
                return redirect(reverse, 'shift_manager/dashboard.html')
        else:
          error = messages.error("Invalid username or password.")
    else:
        error = "Not Registered"
    return render(request, 'shift_manager/login.html', {'error': error})




class DashboardView(TemplateView):
    template_name = 'shift_manager/dashboard.html'


def edit_profile(request):
    employee = get_object_or_404(Employee, user_id=request.user.username)
    if request.method == 'POST':
        # update employee fields
        employee.name = request.POST['name']
        employee.department = Department.objects.get(pk=request.POST['department'])
        employee.category = Category.objects.get(pk=request.POST['category'])
        # save employee changes
        employee.save()
        return redirect('dashboard')
    else:
        # display edit profile form
        departments = Department.objects.all()
        categories = Category.objects.all()
        return render(request, 'shift_manager/edit_profile.html', {'employee': employee, 'departments': departments, 'categories': categories})


# def manage_Shift_time(request):
#     # allow manager to manage Shift_time for all employees
#     return render(request, 'shift_manager/manage_Shift_time.html')


def manage_departments(request):
    # allow manager to manage departments and employees
    return render(request, 'shift_manager/manage_departments.html')


def signout(request):
    logout(request)
    return redirect('login')




def dashboard(request):
    employee = get_object_or_404(Employee, user_id=request.user.username)
    shifts = Shift.objects.filter(employee=employee)
    today = date.today()
    next_day = today + datetime.timedelta(days=1)
    shifts_today = Shift.objects.filter(employee=employee, day=today)
    shifts_next_day = Shift.objects.filter(employee=employee, day=next_day)

    context = {
        'employee': employee,
        'shifts': shifts,
        'shifts_today': shifts_today,
        'shifts_next_day': shifts_next_day,
    }
    return render(request, "shift_manager/dashboard.html", context)


@login_required
def clock_in_out(request):
    employee = request.user.employee
    if employee:
        if employee.is_clocked_in:
            employee.is_clocked_in = False
            employee.clock_out_time = datetime.now()
            employee.current_shift = None
            employee.save()
            Clock.objects.create(employee=employee, clock_in_time=employee.clock_in_time, clock_out_time=employee.clock_out_time)
        else:
            employee.is_clocked_in = True
            employee.clock_in_time = datetime.now()
            employee.current_shift = employee.get_current_shift()
            employee.save()
    return redirect('shift_manager/dashboard.html')


def submit_complaint(request):
    employee = get_object_or_404(Employee, user_id=request.user.username)
    if request.method == 'POST':
        shift_id = request.POST.get('shift')
        complaint_text = request.POST.get('complaint_text')
        shift = Shift.objects.get(pk=shift_id)

        # Create a new Complaint object and link it to the Shift and Employee
        complaint = Complaint.objects.create(employee=employee , shift=shift, complaint_text=complaint_text)

        messages.success(request, 'Complaint submitted successfully!')
    return redirect('dashboard')  # Redirect to the employee dashboard


def authenticated_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('dashboard')

    return _wrapped_view


@authenticated_user
def change_password(request):
    employee = get_object_or_404(Employee, user_id=request.user.username)
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password1 = request.POST['new_password1']
        new_password2 = request.POST['new_password2']

        if request.user.check_password(current_password):
            if new_password1 == new_password2:
                # Update password in User model
                request.user.set_password(new_password1)
                request.user.save()

                # Update password in Employee model (if applicable)
                employee = employee
                if employee:
                    employee.password = new_password1
                    employee.save()

                # Update session authentication hash to avoid log out
                update_session_auth_hash(request, request.user)

                messages.success(request, 'Password changed successfully!')
            else:
                messages.error(request, 'New passwords do not match.')
        else:
            messages.error(request, 'Current password is incorrect.')

    return redirect('dashboard')  # Redirect to the employee dashboard