from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import datetime
from .utils import ai_response, classify_intent

@require_http_methods(["GET", "POST"])
def chatbot_view(request):
    if request.method == 'POST':
        user_message = request.POST.get('user_message', '').strip()
        lm = user_message.lower()

        # INTENT DETECTION
        intent = classify_intent(lm)

        if intent == 'leave_full':
            return JsonResponse({'response': "Please select your leave date using the calendar", 'action': 'show_calendar'})
        elif intent == 'leave_half':
            return JsonResponse({'response': "Please select your leave time using the time picker", 'action': 'show_timepicker'})
        elif intent == 'leave_type':
            return JsonResponse({'response': "Choose leave type: Full Day Leave or Half Day Leave", 'action': 'choose_leave_type'})
        elif lm.startswith('date '):
            try:
                d = datetime.datetime.strptime(lm[5:], "%Y-%m-%d").date()
                return JsonResponse({'response': f"Full-day leave requested for {d}"})
            except ValueError:
                return JsonResponse({'response': "Invalid date format. Please use YYYY-MM-DD"})
        elif lm.startswith('time '):
            try:
                t = datetime.datetime.strptime(lm[5:], "%H:%M").time()
                return JsonResponse({'response': f"Half-day leave requested for {t}"})
            except ValueError:
                return JsonResponse({'response': "Invalid time format. Please use HH:MM"})

        elif intent == 'faq':
            return JsonResponse({'response': "Ask me anything about HR, benefits, or company culture!", 'action': 'faq_mode'})

        elif intent == 'form_travel':
            return JsonResponse({'response': "Let's fill out your travel claim form. What’s your destination?", 'action': 'start_travel_form'})

        elif intent == 'anonymous_feedback':
            return JsonResponse({'response': "You can now share your feedback anonymously.", 'action': 'show_feedback_form'})

        # Fallback to AI
        ai = ai_response(user_message)
        return JsonResponse({'response': ai})

    return render(request, 'chatbot/chatbot.html')


from django.views.decorators.csrf import csrf_exempt
from .models import AnonymousFeedback, TravelForm

@require_http_methods(["POST"])
@csrf_exempt
def submit_feedback(request):
    message = request.POST.get('feedback', '').strip()
    if message:
        AnonymousFeedback.objects.create(message=message)
        return JsonResponse({'status': 'success', 'response': '✅ Your anonymous feedback was submitted.'})
    return JsonResponse({'status': 'fail', 'response': '❌ Feedback cannot be empty.'})

@require_http_methods(["POST"])
@csrf_exempt
def submit_travel_form(request):
    dest = request.POST.get('destination')
    date = request.POST.get('date')
    purpose = request.POST.get('purpose')

    if all([dest, date, purpose]):
        TravelForm.objects.create(destination=dest, date=date, purpose=purpose)
        return JsonResponse({'status': 'success', 'response': '✅ Your travel form was submitted!'})
    return JsonResponse({'status': 'fail', 'response': '❌ All travel form fields are required.'})