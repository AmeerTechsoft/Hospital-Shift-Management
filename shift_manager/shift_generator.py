# from datetime import timedelta, datetime
# from random import shuffle
#
# from django.db.models import Count, Q
#
# from shift_manager.models import Shift, Shift_time, Employee, Department, Category
#
#
# def generate_shifts(days, start_date):
#     for day in range(days):
#         date = start_date + timedelta(days=day)
#         generate_shifts_for_day(date)
#
# def generate_shifts_for_day(date):
#     # Get all departments with at least 2 employees, but exclude departments under Non-Medical category
#     departments = Department.objects.annotate(num_employees=Count('employee')).filter(num_employees__gte=2)
#
#
#     # Shuffle the departments to avoid having the same departments always get the same shift
#     shuffle(departments)
#
#     for department in departments:
#         generate_shifts_for_department(date, department)
#
# def generate_shifts_for_department(date, department):
#     # Get all employees in the department
#     employees = Employee.objects.filter(department=department)
#
#     # Split the employees into two groups: those who are on day shift and those who are on night shift
#     day_shift_employees = employees.filter(shift_type='D')
#     night_shift_employees = employees.filter(shift_type='N')
#
#     # Shuffle the employee lists to avoid having the same employees always get the same shift
#     shuffle(day_shift_employees)
#     shuffle(night_shift_employees)
#
#     # Check if there are at least 2 employees on each shift
#     if len(day_shift_employees) < 2 or len(night_shift_employees) < 2:
#         return
#
#     # Assign the first two employees in each list to the day shift and the remaining employees to the night shift
#     day_shift_employees = day_shift_employees[:2]
#     night_shift_employees = night_shift_employees[2:]
#
#     # Create ShiftTime objects for each employee on the day shift
#     for employee in day_shift_employees:
#         start_time = datetime.combine(date, employee.start_time)
#         end_time = datetime.combine(date, employee.end_time)
#         shift_time = Shift_time.objects.create(user=employee, department=department, shift_type='D', date=date, start_time=start_time, end_time=end_time)
#         create_shift(shift_time)
#
#     # Create ShiftTime objects for each employee on the night shift
#     for employee in night_shift_employees:
#         start_time = datetime.combine(date, employee.start_time)
#         end_time = datetime.combine(date+timedelta(days=1), employee.end_time)
#         shift_time = Shift_time.objects.create(user=employee, department=department, shift_type='N', date=date, start_time=start_time, end_time=end_time)
#         create_shift(shift_time)
#
# def create_shift(shift_time):
#     shift = Shift.objects.create(employee=shift_time.user, start_time=shift_time.start_time, end_time=shift_time.end_time)
#     return shift
#
#

# from datetime import timedelta
#
# from django.utils import timezone
# from .models import Employee, Shift
#
# def generate_schedule(modeladmin, request, queryset):
#     schedule = {}
#     employees = Employee.objects.all()
#     shift_type = list(ShiftType.objects.all())
#     global START_DATE
#
#     # Generate schedule for each department
#     for department in Department.objects.all():
#         department_employees = employees.filter(department=department)
#
#         # Randomly assign shifts to each employee
#         for employee in department_employees:
#             for day in range(NUM_DAYS):
#                 date = START_DATE + timedelta(days=day)
#                 shift = random.choice(shift_type)
#                 shift_obj = Shift.objects.create(employee=employee, day=date, shift_type=shift)
#                 shift_obj.save()
#
#         schedule[department] = [(shift.employee, shift.shift_type) for shift in Shift.objects.filter(employee__in=department_employees)]
#
#     return schedule

def generate_schedule(modeladmin, request, queryset, selected_departments=None, selected_employees=None, selected_categories=None):
    schedule = {}
    shift_type = list(ShiftType.objects.all())
    global START_DATE

    # Generate schedule for each department
    departments = Department.objects.all()
    for department in departments:
        if selected_departments and department not in selected_departments:
            continue

        department_employees = department.employee_set.all()
        if selected_employees:
            department_employees = department_employees.filter(id__in=selected_employees)
        if selected_categories:
            department_employees = department_employees.filter(category__in=selected_categories)

        # Randomly assign shifts to each employee
        for employee in department_employees:
            for day in range(NUM_DAYS):
                date = START_DATE + timedelta(days=day)
                shift = random.choice(shift_type)
                shift_obj = Shift.objects.create(employee=employee, day=date, shift_type=shift)
                shift_obj.save()

        schedule[department] = [(shift.employee, shift.shift_type) for shift in Shift.objects.filter(employee__in=department_employees)]

    return schedule




import random
from datetime import timedelta

from django.utils import timezone
from .models import Employee, Shift, Department, ShiftType

NUM_DAYS = 4  # Number of days to generate shifts for

START_DATE = timezone.now().date()  # Start date for generating shifts


# num_days =5
# def generate_schedule():
#     schedule = {}
#     employees = Employee.objects.all()
#     shift_type = list(ShiftType.objects.all())
#     global START_DATE
#
#     # Generate schedule for each department
#     for department in Department.objects.all():
#         department_employees = employees.filter(department=department)
#
#         # Randomly assign shifts to each employee
#         for employee in department_employees:
#             for day in range(num_days):
#                 date = START_DATE + timedelta(days=day)
#                 shift = random.choice(shift_type)
#                 shift_obj = Shift.objects.create(employee=employee, day=date, shift_type=shift)
#                 shift_obj.save()
#
#         schedule[department] = [(shift.employee, shift.shift_type) for shift in Shift.objects.filter(employee__in=department_employees)]
#
#    # Update START_DATE to add one day for the next schedule generation
#
#     START_DATE = START_DATE + timedelta(days=1)
#     return schedule


# def generate_schedule():
#     employees = list(Employee.objects.all())
#     shift_types = list(ShiftType.objects.all())
#     departments = list(Department.objects.all())
#     num_days = 4
#     global START_DATE
#
#     schedule = []
#     employee_shifts = {employee.id: 0 for employee in employees}
#
#     for day_offset in range(num_days):
#         current_date = START_DATE + timedelta(days=day_offset)
#         shifts_for_day = []
#
#         for department in departments:
#             employees_in_department = [employee for employee in employees if employee.department == department]
#             num_employees = len(employees_in_department)
#
#             if num_employees <= 3:
#                 num_per_shift = 1
#             else:
#                 num_per_shift = 2
#
#             assigned_employees = set()
#             for i in range(len(shift_types)):
#                 num_shifts_filled = 0
#                 while num_shifts_filled < num_per_shift:
#                     # Sort employees by number of assigned shifts
#                     employees_sorted = sorted(
#                         employees_in_department,
#                         key=lambda x: employee_shifts[x.id],
#                     )
#
#                     for employee in employees_sorted:
#                         if employee.id not in assigned_employees:
#                             assigned_employees.add(employee.id)
#                             num_shifts_filled += 1
#                             employee_shifts[employee.id] += 1
#                             shift = Shift(employee=employee, shift_type=shift_types[i], day=current_date)
#                             shifts_for_day.append(shift)
#                             if num_shifts_filled == num_per_shift:
#                                 break
#
#         schedule.append((current_date, shifts_for_day))
#     START_DATE = START_DATE + timedelta(days=1)
#     return schedule

    #

