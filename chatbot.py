"""
chatbot.py
----------
Core chatbot logic for FitBuddy.

Uses a simple but effective intent-matching approach:
  1. Normalize the user's text (lowercase, remove punctuation).
  2. Score each intent by counting how many of its pattern tokens overlap
     with the user's input, weighted by phrase length.
  3. Return a response from the best-matching intent, or a fallback if
     no intent scores above a confidence threshold.

This is all rule-based / lexical — no external ML model, no API keys,
and it runs entirely offline. It's fast, predictable, and easy to extend
by just adding more patterns to intents.json.
"""

import json
import random
import re
import string
from pathlib import Path


class FitBuddyBot:
    def __init__(self, intents_path="intents.json"):
        # Load intents from JSON file
        path = Path(__file__).parent / intents_path
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.intents = data["intents"]

        # Build a lookup: tag -> list of token-sets for each pattern
        # Pre-computing this so we don't re-tokenize on every message.
        self.pattern_index = []
        for intent in self.intents:
            tag = intent["tag"]
            for pattern in intent["patterns"]:
                tokens = self._tokenize(pattern)
                if tokens:
                    self.pattern_index.append({
                        "tag": tag,
                        "tokens": tokens,
                        "length": len(tokens),
                        "raw": pattern
                    })

        # Fallback intent (used when nothing matches well enough)
        self.fallback = next(
            (i for i in self.intents if i["tag"] == "fallback"),
            {"responses": ["Sorry, I didn't understand that."]}
        )

        # Confidence threshold — if the best score is below this,
        # we treat it as unknown and return a fallback.
        self.threshold = 0.34

    @staticmethod
    def _tokenize(text):
        """Lowercase, strip punctuation, split on whitespace."""
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        # Also remove common filler words that don't help matching
        stopwords = {"a", "an", "the", "i", "me", "my", "is", "am", "for",
                     "to", "of", "in", "on", "do", "you", "please", "can",
                     "could", "would", "should", "will"}
        tokens = [t for t in text.split() if t and t not in stopwords]
        return set(tokens)

    def _score_pattern(self, user_tokens, pattern):
        """
        Score a single pattern against the user's token set.
        Returns a value in [0, 1] — fraction of pattern tokens found.
        Also gives a small bonus when the user's phrase is close in length
        to the pattern (prevents very short user messages from over-matching
        long patterns).
        """
        pattern_tokens = pattern["tokens"]
        if not pattern_tokens:
            return 0.0
        overlap = user_tokens & pattern_tokens
        if not overlap:
            return 0.0
        # Base score: what fraction of the pattern's keywords we matched
        score = len(overlap) / len(pattern_tokens)
        # Boost multi-word matches so "chest workout" beats just "chest"
        # when the user explicitly asked "give me a chest workout".
        if len(overlap) >= 2:
            score += 0.15
        return score

    def classify(self, text):
        """Return (best_tag, best_score) for the user's input."""
        user_tokens = self._tokenize(text)
        if not user_tokens:
            return ("fallback", 0.0)

        best_tag = "fallback"
        best_score = 0.0
        for pattern in self.pattern_index:
            score = self._score_pattern(user_tokens, pattern)
            if score > best_score:
                best_score = score
                best_tag = pattern["tag"]

        return (best_tag, best_score)

    def get_response(self, text):
        """Main entry point — take user text, return bot reply."""
        if not text or not text.strip():
            return "Type something and I'll see what I can do!"

        tag, confidence = self.classify(text)

        # Low confidence -> fallback
        if confidence < self.threshold:
            return random.choice(self.fallback["responses"])

        # Find the matching intent and pick a random response
        intent = next((i for i in self.intents if i["tag"] == tag), None)
        if intent and intent.get("responses"):
            return random.choice(intent["responses"])

        return random.choice(self.fallback["responses"])


# Quick manual test if you run this file directly
if __name__ == "__main__":
    bot = FitBuddyBot()
    print("FitBuddy CLI test mode. Type 'quit' to exit.\n")
    while True:
        user = input("You: ").strip()
        if user.lower() in {"quit", "exit"}:
            break
        print(f"Bot: {bot.get_response(user)}\n")
