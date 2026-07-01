const chatbotForm = document.querySelector('#chatbot-form');
const chatbotMessages = document.querySelector('#chatbot-messages');
const chatbotPanel = document.querySelector('#chatbot-panel');
const chatbotToggle = document.querySelector('#chatbot-toggle');
const chatbotClose = document.querySelector('#chatbot-close');
const galleryFallback =
  'data:image/svg+xml;charset=UTF-8,' +
  encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="900" height="600" viewBox="0 0 900 600">
      <rect width="900" height="600" fill="#0f172a"/>
      <rect x="70" y="70" width="760" height="460" rx="24" fill="#1e293b"/>
      <circle cx="250" cy="230" r="70" fill="#22d3ee"/>
      <path d="M120 490 330 310l130 110 110-90 210 160Z" fill="#818cf8"/>
      <text x="450" y="125" fill="#f8fafc" font-family="Arial, sans-serif" font-size="36" text-anchor="middle">AI-Solutions Gallery</text>
      <text x="450" y="175" fill="#cbd5e1" font-family="Arial, sans-serif" font-size="22" text-anchor="middle">Promotional event image</text>
    </svg>
  `);

document.querySelectorAll('.gallery-image').forEach((image) => {
  image.addEventListener('error', () => {
    image.src = galleryFallback;
  }, { once: true });
});

if (chatbotPanel && chatbotToggle) {
  const setChatbotOpen = (isOpen) => {
    chatbotPanel.classList.toggle('hidden', !isOpen);
    chatbotToggle.setAttribute('aria-expanded', String(isOpen));

    if (isOpen) {
      chatbotForm?.querySelector('input[name="message"]')?.focus();
    }
  };

  chatbotToggle.addEventListener('click', () => {
    setChatbotOpen(chatbotPanel.classList.contains('hidden'));
  });

  chatbotClose?.addEventListener('click', () => {
    setChatbotOpen(false);
    chatbotToggle.focus();
  });
}

if (chatbotForm) {
  chatbotForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const input = chatbotForm.querySelector('input[name="message"]');
    const userMessage = input.value.trim();
    if (!userMessage) {
      return;
    }

    const userBubble = document.createElement('div');
    userBubble.className = 'rounded-3xl bg-indigo-600 text-white p-4 mb-3 max-w-xl';
    userBubble.textContent = userMessage;
    chatbotMessages.appendChild(userBubble);

    let data = { reply: 'Sorry, I could not respond just now. Please use the Contact page for help.' };
    try {
      const response = await fetch('/chatbot-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });
      data = await response.json();
    } catch (error) {
      data.reply = 'Sorry, I could not respond just now. Please use the Contact page for help.';
    }
    const botBubble = document.createElement('div');
    botBubble.className = 'rounded-3xl bg-slate-100 text-slate-900 p-4 mb-3 max-w-xl';
    botBubble.textContent = data.reply;
    chatbotMessages.appendChild(botBubble);
    input.value = '';
  });
}
