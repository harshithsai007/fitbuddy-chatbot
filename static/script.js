/* FitBuddy frontend logic
   - Sends messages to /chat and renders replies
   - Shows a typing indicator while waiting
   - Supports the browser's SpeechRecognition API for voice input
*/

const chatWindow = document.getElementById("chatWindow");
const chatForm   = document.getElementById("chatForm");
const userInput  = document.getElementById("userInput");
const micBtn     = document.getElementById("micBtn");
const clearBtn   = document.getElementById("clearBtn");
const suggestions = document.getElementById("suggestions");

// ---------- Rendering ----------

function addMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = `message ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = sender === "bot" ? "💪" : "🙂";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = text; // textContent avoids XSS from user input

    msg.appendChild(avatar);
    msg.appendChild(bubble);
    chatWindow.appendChild(msg);

    // Auto-scroll to newest message
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function addTypingIndicator() {
    const msg = document.createElement("div");
    msg.className = "message bot";
    msg.id = "typingIndicator";

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "💪";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';

    msg.appendChild(avatar);
    msg.appendChild(bubble);
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function removeTypingIndicator() {
    const t = document.getElementById("typingIndicator");
    if (t) t.remove();
}

// ---------- Sending messages ----------

async function sendMessage(text) {
    if (!text || !text.trim()) return;

    addMessage(text, "user");
    userInput.value = "";
    addTypingIndicator();

    try {
        // Small artificial delay so the typing indicator is visible on fast replies.
        // Makes the convo feel natural instead of instant/jarring.
        const [res] = await Promise.all([
            fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text })
            }),
            new Promise(r => setTimeout(r, 400))
        ]);

        const data = await res.json();
        removeTypingIndicator();
        addMessage(data.reply || "Something went wrong on my end.", "bot");
    } catch (err) {
        removeTypingIndicator();
        addMessage("Can't reach the server. Make sure the Flask app is running.", "bot");
        console.error(err);
    }
}

// Form submit (Enter key or Send button)
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage(userInput.value);
});

// Suggestion chips
suggestions.addEventListener("click", (e) => {
    if (e.target.classList.contains("chip")) {
        const text = e.target.dataset.msg;
        sendMessage(text);
    }
});

// Clear chat (keeps only the opening bot message)
clearBtn.addEventListener("click", () => {
    // Remove every message except the first (greeting)
    const messages = chatWindow.querySelectorAll(".message");
    messages.forEach((m, i) => { if (i > 0) m.remove(); });
});

// ---------- Voice input (Web Speech API) ----------

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    let listening = false;

    micBtn.addEventListener("click", () => {
        if (listening) {
            recognition.stop();
            return;
        }
        recognition.start();
    });

    recognition.addEventListener("start", () => {
        listening = true;
        micBtn.classList.add("listening");
        userInput.placeholder = "Listening...";
    });

    recognition.addEventListener("end", () => {
        listening = false;
        micBtn.classList.remove("listening");
        userInput.placeholder = "Ask for a workout, a tip, or type 'help'...";
    });

    recognition.addEventListener("result", (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        sendMessage(transcript);
    });

    recognition.addEventListener("error", (e) => {
        console.warn("Speech recognition error:", e.error);
        listening = false;
        micBtn.classList.remove("listening");
    });
} else {
    // Browser doesn't support speech recognition (e.g. Firefox) — hide the mic
    micBtn.style.display = "none";
}
