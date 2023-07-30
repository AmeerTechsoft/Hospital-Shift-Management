from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta



# Register your models here.
from .models import Employee, Category, Department, Shift, ShiftType, Complaint
from .shift_generator import generate_schedule, START_DATE


def generate_schedule_action(modeladmin, request, queryset):
    # Call the generate_schedule function
    schedule = generate_schedule()
    # Redirect back to the changelist page
    return HttpResponseRedirect(request.get_full_path())


class EmployeeAdmin(admin.ModelAdmin):
    actions = [generate_schedule_action]



class EmployeeInline(admin.TabularInline):
    model = Employee


class DepartmentInline(admin.TabularInline):
    model = Department


class CategoryAdmin(admin.ModelAdmin):
    inlines = [DepartmentInline]
    actions = [generate_schedule]


class DepartmentAdmin(admin.ModelAdmin):
    inlines = [EmployeeInline]
    actions = [generate_schedule]

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', 'email', 'department')
    list_filter = ('department',) # filter by department
    search_fields = ('user_id', 'email')
    actions = [generate_schedule]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif request.user.is_staff:
            department = request.user.employee.department
            category = department.category
            return qs.filter(department=department, category=category)
        else:
            return qs.none()


# class EmployeeAdmin(UserAdmin):
#     inlines = [ShiftInline]

class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['employee', 'shift', 'is_resolved']
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        messages.info(request, 'Complaints marked as resolved.')

    mark_as_resolved.short_description = 'Mark selected complaints as resolved'

class ShiftAdmin(admin.ModelAdmin):
    list_display = ['employee', 'shift_type', 'day']
    list_filter = ['shift_type']

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if '_saveasnew' not in request.POST and '_continue' not in request.POST:
            # Check if the shift has a complaint
            complaint = Complaint.objects.filter(shift=obj).exists()
            if complaint:
                messages.info(request, 'New message received: Complaint from an employee')
        return response

admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(Shift, ShiftAdmin)
admin.site.register(ShiftType)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.unregister(Group)
# admin.site.register(EmployeeListView)