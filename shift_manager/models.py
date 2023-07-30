import phonenumbers
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.views.generic import ListView
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from phonenumbers.phonenumberutil import NumberParseException


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.name}'


class DepartmentManager(models.Manager):
    def for_category(self, category):
        return self.filter(category=category)


class Department(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    objects = DepartmentManager()

    def __str__(self):
        return f'{self.name}'


class Employee(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user_id = models.CharField(max_length=10, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    other_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)  # Add the address field
    date_of_birth = models.DateField()  # Add the date_of_birth field
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)  # Add the gender field
    image = models.ImageField(upload_to='worker_images/')
    password = models.CharField(max_length=128, default='')



    def save(self, *args, **kwargs):
        try:
            parsed_number = phonenumbers.parse(self.phone_number, 'NG')
            formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            self.phone_number = formatted_number
        except NumberParseException:
            pass

        super().save(*args, **kwargs)
    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.user_id}'


@receiver(pre_save, sender=Employee)
def generate_user_id(sender, instance, **kwargs):
    """
    Generate a unique user ID for each worker based on their department
    and save it to the instance before saving to the database.
    """

    if not instance.user_id:
        department_words = instance.department.name.split()
        department_prefix = "".join(word[0].upper() for word in department_words)
        max_id = Employee.objects.filter(
            department=instance.department
        ).aggregate(models.Max('user_id'))['user_id__max'] or f"{department_prefix}/00000"
        max_prefix, max_number = max_id.split('/')
        new_number = int(max_number) + 1
        new_id = f"{department_prefix}/{str(new_number).zfill(5)}"
        instance.user_id = new_id


@receiver(pre_save, sender=Employee)
def set_default_password(sender, instance, **kwargs):
    """
    Set the default password to the worker's last name in capital letters.
    """
    if not instance.password:
        instance.password = instance.last_name.upper()


class ShiftType(models.Model):
    SHIFT_CHOICES = [
        ('M', 'Morning'),
        ('A', 'Afternoon'),
        ('N', 'Night'),
    ]
    start_time = models.TimeField()
    end_time = models.TimeField()
    shift_type = models.CharField(max_length=1, choices=SHIFT_CHOICES)

    def __str__(self):
        return f"{self.get_shift_type_display()} ({self.start_time.strftime('%I:%M %p')} - {self.end_time.strftime('%I:%M %p')})"


class Shift(models.Model):
    SHIFT_CHOICES = [
        ('M', 'Morning'),
        ('A', 'Afternoon'),
        ('N', 'Night'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift_type = models.ForeignKey(ShiftType, on_delete=models.PROTECT)
    day = models.DateField()

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} ({self.day.strftime('%Y-%m-%d')}) - {self.shift_type}"

# class Employee_user(AbstractUser):
#     # Add custom fields
#     user_id = Employee.user_id
#     password = Employee.password
#     department = Employee.department
#     category = Employee.category
#
#     # Use user_id as the username field
#     USERNAME_FIELD = 'user_id'
#     PASSWORD_FIELD = 'password'
#
#     # Add department to the required fields for user creation
#     REQUIRED_FIELDS = ['user_id', 'password', 'department', 'category']


class Employee_user(AbstractUser):
        # Add custom fields
    user_id = Employee.user_id
    password = Employee.password
    department = Employee.department

    # Use user_id as the username field
    USERNAME_FIELD = 'user_id'
    PASSWORD_FIELD = 'password'

    # Add department to the required fields for user creation
    REQUIRED_FIELDS = ['user_id', 'password', 'department', 'category']

    # Add a related_name argument to avoid clash with User model
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='employee_users',  # related_name added here
        related_query_name='employee_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='employee_users',  # related_name added here
        related_query_name='employee_user',
    )

    def __str__(self):
        return self.user_id

@receiver(post_save, sender=Employee)
def create_employee_user(sender, instance, created, **kwargs):
    if created:
        User = get_user_model()
        user = User.objects.create_user(
            username=instance.user_id,
            password=instance.password,
            email=instance.email,
            first_name=instance.first_name,
            last_name=instance.last_name,
            is_staff=True
        )
        # employee_user = Employee_user.objects.create(
        #     user=user,
        #     user_id=instance.user_id,
        #     first_name=instance.first_name,
        #     last_name=instance.last_name,
        #     email=instance.email,
        #     password=instance.password,
        #     department=instance.department,
        #     category=instance.category
        # )






@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employee_list.html'
    context_object_name = 'employees'
    paginate_by = 10



class Clock(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.shift} - {self.clock_in} - {self.clock_out}"




class Complaint(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    complaint_text = models.TextField()
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Complaint from {self.employee} about {self.shift}"