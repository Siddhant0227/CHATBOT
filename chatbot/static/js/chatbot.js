document.addEventListener('DOMContentLoaded', () => {
    const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    const messagesDiv = document.getElementById('messages');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user_message');

    flatpickr("#leave_date", { dateFormat: "Y-m-d", minDate: "today" });
    flatpickr("#leave_time", {
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i",
        time_24hr: true
    });

    function appendMessage(text, isUser = false, isSuccess = false) {
        const msg = document.createElement('div');
        msg.className = `message ${isUser ? 'user-message' : 'bot-message'} ${isSuccess ? 'success' : ''}`;
        msg.innerHTML = text;
        messagesDiv.appendChild(msg);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    async function sendMessageToServer(message) {
        appendMessage(message, true);

        const loading = document.createElement('div');
        loading.className = 'message bot-message loading';
        loading.innerHTML = `<div class="dot-flashing"><div></div><div></div><div></div></div>`;
        messagesDiv.appendChild(loading);

        try {
            const res = await fetch('/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                },
                body: `user_message=${encodeURIComponent(message)}`
            });

            const data = await res.json();
            loading.remove();
            appendMessage(data.response);
            if (data.action) handleAction(data.action);
        } catch (err) {
            loading.remove();
            console.error(err);
            appendMessage("Sorry, there was an error. Please try again.");
        }
    }

    function handleAction(action) {
        document.getElementById('calendar').style.display = 'none';
        document.getElementById('timepicker').style.display = 'none';
        document.getElementById('choice-buttons').style.display = 'none';
        document.getElementById('feedback-form').style.display = 'none';
        document.getElementById('travel-form').style.display = 'none';

        if (action === 'show_calendar') {
            document.getElementById('calendar').style.display = 'block';
        } else if (action === 'show_timepicker') {
            document.getElementById('timepicker').style.display = 'block';
        } else if (action === 'choose_leave_type') {
            document.getElementById('choice-buttons').style.display = 'flex';
        } else if (action === 'faq_mode') {
            appendMessage(`
                <ul>
                    <li>💼 What’s the dress code?</li>
                    <li>🧾 How do I raise a concern?</li>
                    <li>🏖️ What are the benefits?</li>
                </ul>
            `);
        } else if (action === 'start_travel_form') {
            document.getElementById('travel-form').style.display = 'block';
        } else if (action === 'show_feedback_form') {
            document.getElementById('feedback-form').style.display = 'block';
        }
    }

    window.sendMessageFromOption = (opt) => sendMessageToServer(opt);

    window.askLeaveType = () => {
        document.getElementById('feature-buttons').style.display = 'none';
        document.getElementById('choice-buttons').style.display = 'flex';
        sendMessageToServer("leave options");
    };

    window.sendChoice = (choice) => {
        document.getElementById('choice-buttons').style.display = 'none';
        sendMessageToServer(choice);
    };

    window.submitLeaveDate = () => {
        const d = document.getElementById('leave_date').value;
        if (d) {
            document.getElementById('calendar').style.display = 'none';
            document.getElementById('leave_date').value = '';
            sendMessageToServer(`date ${d}`);
        }
    };

    window.submitLeaveTime = () => {
        const t = document.getElementById('leave_time').value;
        if (t) {
            document.getElementById('timepicker').style.display = 'none';
            document.getElementById('leave_time').value = '';
            sendMessageToServer(`time ${t}`);
        }
    };

    window.submitFeedback = async () => {
        const feedback = document.getElementById('feedback_input').value.trim();
        if (!feedback) return appendMessage("❌ Feedback cannot be empty.");

        const formData = new FormData();
        formData.append('feedback', feedback);

        const res = await fetch('/submit-feedback/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: formData
        });

        const data = await res.json();
        appendMessage(data.response);  // Show success or failure response
        document.getElementById('feedback_input').value = '';  // Clear the feedback input field
        document.getElementById('feedback-form').style.display = 'none';  // Hide feedback form after submission

        // Optionally, you can re-enable the features (like the feature buttons) after feedback submission
        document.getElementById('feature-buttons').style.display = 'block'; 
    };

    window.submitTravelForm = async () => {
        const dest = document.getElementById('travel_destination').value;
        const date = document.getElementById('travel_date').value;
        const purpose = document.getElementById('travel_purpose').value;

        if (!(dest && date && purpose)) {
            return appendMessage("❌ Please fill all fields in the travel form.");
        }

        const formData = new FormData();
        formData.append('destination', dest);
        formData.append('date', date);
        formData.append('purpose', purpose);

        const res = await fetch('/submit-travel-form/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: formData
        });

        const data = await res.json();
        appendMessage(data.response);
        document.getElementById('travel-form').style.display = 'none';
        document.getElementById('travel_destination').value = '';
        document.getElementById('travel_date').value = '';
        document.getElementById('travel_purpose').value = '';
    };

    chatForm.addEventListener('submit', e => {
        e.preventDefault();
        const msg = userInput.value.trim();
        if (msg) {
            sendMessageToServer(msg);
            userInput.value = '';
        }
    });
});
