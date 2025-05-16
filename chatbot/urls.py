from django.urls import path
from .views import chatbot_view, submit_feedback, submit_travel_form

urlpatterns = [
    path('', chatbot_view, name='chatbot'),
    path('submit-feedback/', submit_feedback, name='submit_feedback'),
    path('submit-travel-form/', submit_travel_form, name='submit_travel_form'),
]
