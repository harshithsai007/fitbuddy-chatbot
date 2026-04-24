# FitBuddy — CSE 491 Honors Option Project

A conversational fitness chatbot that helps college students build quick workouts, target specific muscle groups, and get simple training/nutrition tips. Built for the CSE 491 Honors Option Project.

## What it does

Ask it things like:
- `Give me a chest workout`
- `15 minute workout`
- `Beginner plan`
- `Leg day`
- `How much protein do I need?`
- `I'm unmotivated`
- `Home workout, no equipment`

It also has a **voice input** button (🎤) — works in Chrome/Edge/Safari via the browser's Web Speech API.

## How it works

- **Backend:** Python + Flask
- **NLP:** Custom rule-based intent classifier in `chatbot.py`
  - Tokenizes user input (lowercase, remove punctuation, drop stopwords)
  - Scores every intent's patterns by keyword overlap + multi-word bonus
  - Returns the best-matching intent's response, or a fallback if confidence is low
- **Knowledge base:** `intents.json` — 20+ intents covering greetings, workouts by goal/muscle/time, nutrition, rest, and motivation
- **Frontend:** Vanilla HTML/CSS/JavaScript — clean chat UI, typing indicator, suggestion chips, voice input

No external APIs, no API keys, no internet required. Everything runs locally.

## Setup

1. Make sure you have Python 3.8 or newer installed.

2. Install the one dependency (Flask):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Open your browser to **http://localhost:5000**

That's it. The chatbot should be ready to use.

## Project structure

```
honors-medasani/
├── app.py                # Flask server
├── chatbot.py            # Intent classifier + response logic
├── intents.json          # Knowledge base (patterns + responses)
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Chat UI markup
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend logic + voice input
└── README.md             # This file
```

## Testing the classifier directly

If you just want to test the bot logic without the web UI:
```bash
python chatbot.py
```
That starts a CLI where you can type messages and see replies.

## Author

Harshith Sai Medasani — CSE 491, Spring 2026
