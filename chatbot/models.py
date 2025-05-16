from django.db import models

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('full', 'Full Day'),
        ('half', 'Half Day'),
    ]

    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    leave_date = models.DateField(null=True, blank=True)
    leave_time = models.TimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.leave_type.capitalize()} Leave on {self.leave_date or self.leave_time}"
class AnonymousFeedback(models.Model):
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback on {self.submitted_at}"

class TravelForm(models.Model):
    destination = models.CharField(max_length=255)
    date = models.DateField()
    purpose = models.CharField(max_length=500)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.destination} on {self.date}"