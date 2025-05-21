# chatbot/models.py

from django.db import models
from django.utils import timezone

class Employee(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('full', 'Full Day'),
        ('half', 'Half Day'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    leave_date = models.DateField(default=timezone.now)
    leave_time = models.TimeField(null=True, blank=True)  # only for half day
    requested_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        time_str = self.leave_time.strftime('%H:%M') if self.leave_time else 'N/A'
        return f"{self.employee.name} - {self.leave_type} leave on {self.leave_date} at {time_str}"
