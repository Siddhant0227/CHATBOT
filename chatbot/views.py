from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import datetime
from .models import LeaveRequest, Employee
from .utils import ai_response, classify_intent

@require_http_methods(["GET", "POST"])
def chatbot_view(request):
    try:
        if request.method == 'POST':
            user_message = request.POST.get('user_message', '').strip()
            if not user_message:
                return JsonResponse({'response': 'Please enter a message.', 'action': None})

            lm = user_message.lower()
            print(f"[DEBUG] Received message: '{user_message}'")

            session = request.session

            # If employee is not identified yet, treat input as their name
            if 'employee_id' not in session:
                try:
                    employee, created = Employee.objects.get_or_create(name=user_message.title())
                except Exception as e:
                    print(f"[ERROR] Employee get_or_create failed: {e}")
                    return JsonResponse({
                        'response': 'Server error creating employee record. Please contact admin.'
                    }, status=500)

                session['employee_id'] = employee.id
                session['state'] = 'ask_leave_type'

                return JsonResponse({
                    'response': f"Hello {employee.name}! Please choose leave type: Full Day or Half Day.",
                    'action': 'choose_leave_type'
                })

            # Get employee from session
            try:
                employee = Employee.objects.get(id=session['employee_id'])
            except Employee.DoesNotExist:
                session.flush()
                return JsonResponse({
                    'response': 'Session expired or employee not found. Please refresh and start again.'
                }, status=400)

            state = session.get('state')

            # Quick FAQ responses
            if "dress code" in lm:
                return JsonResponse({
                    'response': "Our dress code is business casual from Monday to Thursday and casual on Fridays.",
                    'action': None
                })

            if any(word in lm for word in ["raise a concern", "report", "complaint"]):
                return JsonResponse({
                    'response': "You can raise concerns anonymously through our HR portal or speak directly to your manager.",
                    'action': None
                })

            if "benefits" in lm:
                return JsonResponse({
                    'response': "We offer health insurance, paid time off, wellness programs, and more!",
                    'action': None
                })

            # Print leave summary anytime
            if lm == 'print':
                leaves = LeaveRequest.objects.filter(employee=employee).order_by('-requested_at')
                if not leaves.exists():
                    response_text = "You have no leave requests."
                else:
                    full_days = leaves.filter(leave_type='full').count()
                    half_days = leaves.filter(leave_type='half').count()
                    response_text = (f"{employee.name}, you have taken:\n"
                                     f"Full day leaves: {full_days}\n"
                                     f"Half day leaves: {half_days}")

                session.flush()  # clear session after print
                return JsonResponse({'response': response_text, 'action': None})

            # Reset conversation to ask leave type
            if lm == 'add more':
                session['state'] = 'ask_leave_type'
                return JsonResponse({
                    'response': "Please choose leave type: Full Day or Half Day.",
                    'action': 'choose_leave_type'
                })

            # Handle states
            if state == 'ask_leave_type':
                if 'full' in lm:
                    session['leave_type'] = 'full'
                    session['state'] = 'ask_leave_date'
                    return JsonResponse({
                        'response': "Please enter the leave date (YYYY-MM-DD).",
                        'action': 'ask_date'
                    })
                elif 'half' in lm:
                    session['leave_type'] = 'half'
                    session['state'] = 'ask_leave_date'
                    return JsonResponse({
                        'response': "Please enter the leave date (YYYY-MM-DD) for your half day leave.",
                        'action': 'ask_date'
                    })
                else:
                    return JsonResponse({
                        'response': "Please specify 'Full Day' or 'Half Day' leave.",
                        'action': 'choose_leave_type'
                    })

            elif state == 'ask_leave_date':
                try:
                    d = datetime.datetime.strptime(user_message, "%Y-%m-%d").date()
                    session['leave_date'] = str(d)
                    if session['leave_type'] == 'full':
                        LeaveRequest.objects.create(employee=employee, leave_type='full', leave_date=d)
                        session['state'] = 'ask_more_or_print'
                        return JsonResponse({
                            'response': f"Full day leave requested for {d}. Would you like to add more leaves or print your leave report? (type 'add more' or 'print')",
                            'action': None
                        })
                    else:
                        session['state'] = 'ask_leave_time'
                        return JsonResponse({
                            'response': "Please enter the leave time (HH:MM, 24-hour format) for your half day leave.",
                            'action': 'ask_time'
                        })
                except ValueError:
                    return JsonResponse({
                        'response': "Invalid date format. Please use YYYY-MM-DD.",
                        'action': 'ask_date'
                    })

            elif state == 'ask_leave_time':
                try:
                    t = datetime.datetime.strptime(user_message, "%H:%M").time()
                    d = datetime.datetime.strptime(session['leave_date'], "%Y-%m-%d").date()
                    LeaveRequest.objects.create(employee=employee, leave_type='half', leave_date=d, leave_time=t)
                    session['state'] = 'ask_more_or_print'
                    return JsonResponse({
                        'response': f"Half day leave requested for {session['leave_date']} at {t.strftime('%H:%M')}. Would you like to add more leaves or print your leave report? (type 'add more' or 'print')",
                        'action': None
                    })
                except ValueError:
                    return JsonResponse({
                        'response': "Invalid time format. Please use HH:MM (24-hour format).",
                        'action': 'ask_time'
                    })

            # Check leave request status
            if "check status" in lm:
                leaves = LeaveRequest.objects.filter(employee=employee).order_by('-requested_at')
                if not leaves.exists():
                    return JsonResponse({'response': "No leave requests found.", 'action': None})

                response_lines = ["Your leave requests:"]
                for leave in leaves:
                    leave_time = leave.leave_time.strftime("%H:%M") if leave.leave_time else "N/A"
                    response_lines.append(f"- {leave.leave_type.title()} leave on {leave.leave_date} at {leave_time}")
                return JsonResponse({
                    'response': "\n".join(response_lines),
                    'action': None
                })

            # Intent classification fallback
            intent = classify_intent(lm)
            print(f"[DEBUG] Classified intent: {intent}")

            if intent == 'leave_type':
                session['state'] = 'ask_leave_type'
                return JsonResponse({
                    'response': "Please choose leave type: Full Day or Half Day.",
                    'action': 'choose_leave_type'
                })

            if intent == 'faq':
                return JsonResponse({
                    'response': (
                        "Here are some support questions you can ask:\n"
                        "💼 What’s the dress code?\n"
                        "🧾 How do I raise a concern?\n"
                        "🏖️ What are the benefits?"
                    ),
                    'action': 'faq_mode'
                })

            # AI fallback
            ai = ai_response(user_message)
            print(f"[DEBUG] AI response: {ai}")
            return JsonResponse({
                'response': ai,
                'action': None
            })

        # For GET requests, render the chatbot interface
        return render(request, 'chatbot/chatbot.html')

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'response': f'Server error: {str(e)}'}, status=500)
