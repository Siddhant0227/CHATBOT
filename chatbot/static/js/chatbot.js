document.addEventListener('DOMContentLoaded', () => {
  const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  const messagesDiv = document.getElementById('messages');
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user_message');
  const goBackContainer = document.getElementById('go-back-container');
  const goBackBtn = document.getElementById('go-back-btn');

  const historyStack = [];
  window.userName = null; // global to hold user name

  flatpickr("#leave_date", { dateFormat: "Y-m-d", minDate: "today" });
  flatpickr("#leave_time", {
    enableTime: true,
    noCalendar: true,
    dateFormat: "H:i",
    time_24hr: true,
  });

  function appendMessage(text, isUser = false, isSuccess = false) {
    const msg = document.createElement('div');
    msg.className = `message ${isUser ? 'user-message' : 'bot-message'} ${isSuccess ? 'success' : ''}`;
    msg.innerHTML = text;
    messagesDiv.appendChild(msg);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  function showGoBackIfNeeded() {
    goBackContainer.style.display = historyStack.length > 1 ? 'block' : 'none';
  }

  function hideAllOptionalUI() {
    ['calendar', 'timepicker', 'choice-buttons', 'faq-buttons', 'user-name-container'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = 'none';
    });
  }

  async function sendMessageToServer(message, addToHistory = true) {
    appendMessage(message, true);
    if (addToHistory) historyStack.push(message);
    showGoBackIfNeeded();

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
        body: `user_message=${encodeURIComponent(message)}`,
      });

      const data = await res.json();
      loading.remove();
      appendMessage(data.response);

      if (data.action) {
        handleAction(data.action);
      } else {
        hideAllOptionalUI();
        document.getElementById('feature-buttons').style.display = 'flex';
      }
    } catch (err) {
      loading.remove();
      console.error(err);
      appendMessage("Sorry, there was an error. Please try again.");
    }
  }

  goBackBtn.addEventListener('click', () => {
    if (historyStack.length <= 1) return;

    historyStack.pop();
    const prevMessage = historyStack[historyStack.length - 1];

    messagesDiv.innerHTML = '';
    appendMessage("Hello! I’m your HR assistant. How can I help you today?");

    hideAllOptionalUI();
    document.getElementById('feature-buttons').style.display = 'flex';

    // Reset username if you want to clear on going back
    // window.userName = null;

    sendMessageToServer(prevMessage, false);
    showGoBackIfNeeded();
  });

  function showFAQOptions() {
    const faqButtonsDiv = document.getElementById('faq-buttons');
    faqButtonsDiv.innerHTML = `
      <button class="btn-feature" onclick="sendMessageFromOption('What’s the dress code?')">💼 What’s the dress code?</button>
      <button class="btn-feature" onclick="sendMessageFromOption('How do I raise a concern?')">🧾 How do I raise a concern?</button>
      <button class="btn-feature" onclick="sendMessageFromOption('What are the benefits?')">🏖️ What are the benefits?</button>
      <button class="btn-feature" onclick="hideFAQOptions()">Back</button>
    `;
    faqButtonsDiv.style.display = 'flex';
    document.getElementById('feature-buttons').style.display = 'none';
  }

  function hideFAQOptions() {
    document.getElementById('faq-buttons').style.display = 'none';
    document.getElementById('feature-buttons').style.display = 'flex';
  }

  function handleAction(action) {
    hideAllOptionalUI();

    if (action === 'show_calendar') {
      const cal = document.getElementById('calendar');
      if (cal) cal.style.display = 'block';
      document.getElementById('feature-buttons').style.display = 'none';
    } else if (action === 'show_timepicker') {
      const tp = document.getElementById('timepicker');
      if (tp) tp.style.display = 'block';
      document.getElementById('feature-buttons').style.display = 'none';
    } else if (action === 'choose_leave_type') {
      const choices = document.getElementById('choice-buttons');
      if (choices) choices.style.display = 'flex';
      document.getElementById('feature-buttons').style.display = 'none';
    } else if (action === 'faq_mode') {
      showFAQOptions();
      return;
    }

    if (action !== 'faq_mode') {
      document.getElementById('feature-buttons').style.display = 'flex';
    }
  }

  window.sendMessageFromOption = (opt) => sendMessageToServer(opt);

  window.askUserName = () => {
    hideAllOptionalUI();
    document.getElementById('feature-buttons').style.display = 'none';

    const nameContainer = document.getElementById('user-name-container');
    if (nameContainer) nameContainer.style.display = 'block';
  };

  window.submitUserName = () => {
    const input = document.getElementById('user_name');
    const name = input.value.trim();
    if (!name) {
      alert("Please enter your name.");
      return;
    }

    document.getElementById('user-name-container').style.display = 'none';
    window.userName = name;

    appendMessage(`Name recorded as: <b>${name}</b>`, true, true);

    // Show leave type choices after name input
    const choices = document.getElementById('choice-buttons');
    if (choices) choices.style.display = 'flex';

    sendMessageToServer(`My name is ${name}. I want to apply for leave.`);
  };

  window.sendChoice = (choice) => {
    const choices = document.getElementById('choice-buttons');
    if (choices) choices.style.display = 'none';

    const message = window.userName ? `${window.userName} requests ${choice}` : choice;
    sendMessageToServer(message);
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

  chatForm.addEventListener('submit', e => {
    e.preventDefault();
    const msg = userInput.value.trim();
    if (msg) {
      sendMessageToServer(msg);
      userInput.value = '';
    }
  });

  appendMessage("Hello! I’m your HR assistant. How can I help you today?");
  historyStack.push("hello");
  showGoBackIfNeeded();
});
