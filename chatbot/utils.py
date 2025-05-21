import os
import requests

def classify_intent(msg):
    """
    Simple keyword-based intent classifier for HR chatbot.
    """
    msg = msg.lower().strip()
    if any(kw in msg for kw in ['full day', 'day off']):
        return 'leave_full'
    elif any(kw in msg for kw in ['half day']):
        return 'leave_half'
    elif 'leave' in msg:
        return 'leave_type'
    elif any(kw in msg for kw in ['raise a concern', 'dress code', 'hr policy', 'culture', 'benefits']):
        return 'faq'
    elif 'travel claim' in msg or 'reimbursement' in msg or 'appraisal form' in msg:
        return 'form_travel'
    elif 'share feedback' in msg or 'anonymously' in msg:
        return 'anonymous_feedback'
    return 'unknown'


def ai_response(user_message):
    """
    Calls Groq's LLaMA 3 API to get AI-generated response.
    """
    try:
        api_key = os.environ.get("GROQ_API_KEY")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "You are a helpful HR assistant."},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 150,
            "temperature": 0.7
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=data
        )

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Sorry, I couldn't process your request right now. Error: {str(e)}"
