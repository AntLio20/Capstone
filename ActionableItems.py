# File Name: ActionableItems.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Functions to locate actionable items and output the list of actionable items

# Required commands:
# Install spacy: pip install spacy

import spacy
from spacy.matcher import Matcher
import re

# Load SpaCy English model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print("Error loading SpaCy model:", e)

# Function to identify actionable sentences and replace "I" with speaker's name
def actionableItems(transcript):
    # Initialize the matcher and add patterns for actionable phrases
    matcher = Matcher(nlp.vocab)
    actionable_patterns = [
        [{"LOWER": "follow"}, {"LOWER": "up"}],
        [{"LOWER": "schedule"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "complete"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "send"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "review"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "update"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "finalize"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "add"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "analyze"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "analyse"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "attend"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "collect"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "compile"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "compute"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "construct"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "copy"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "coordinate"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "delegate"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "develop"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "distribute"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "draft"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "edit"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "establish"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "evaluate"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "execute"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "extract"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "facilitate"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "find"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "formulate"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "initiate"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "inspect"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "interview"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "investigate"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "locate"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "maintain"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "make"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "manage"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "measure"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "merge"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "notify"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "obtain"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "organize"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "perform"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "prepare"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "request"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "research"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "revise"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "search"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "secure"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "select"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "study"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "submit"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "train"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "type"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "verify"}, {"IS_ALPHA": True, "OP": "?"}],
        [{"LOWER": "write"}, {"IS_ALPHA": True, "OP": "?"}]
    ]
    matcher.add("ActionableItems", actionable_patterns)

    context_indicators = ["after the meeting", "next session", "later", "next week", "subsequent", "subsquently",
                          "follow-up", "next meeting", "next month", "tomorrow", "today", "tonight",
                          "this afternoon", "this evening", "follow up", "deadline", "due date"]

    # Initialize variables
    actionable_sentences = set()  # Use a set to avoid duplicates
    current_speaker = None

    # Split the transcript into lines
    lines = transcript.splitlines()

    # Process each line in the transcript
    for i, line in enumerate(lines):
        # Detect timestamp line and skip if found
        timestamp_match = re.match(r"^\d+:\d+:\d+\.\d+\s-->\s\d+:\d+:\d+\.\d+$", line)
        # Following if not statement FOR TESTING ONLY since transcripts from chatgpt have two spaces after every line
        # Remove these lines for final submission that only works with microsoft teams transcripts
        if not timestamp_match:
            timestamp_match = re.match(r"^\d+:\d+:\d+\.\d+\s-->\s\d+:\d+:\d+\.\d+\s\s$", line)
        if timestamp_match:
            continue

        # Detect speaker line and capture full name of speaker
        # Or statement clause FOR TESTING ONLY, remove for final submission
        if i > 0 and (re.match(r"^[A-Za-z]+\s[A-Za-z]+$", line) or re.match(r"^[A-Za-z]+\s[A-Za-z]+\s\s$", line)):
            current_speaker = line
            continue

        # Process the text (assumes text follows the speaker's name line)
        if current_speaker and line.strip():
            text = line.strip()
            doc = nlp(text)
            # Flag to track if sentence was added
            actionable_sentence_added = False

            for match_id, start, end in matcher(doc):
                span = doc[start:end]
                # Get the entire sentence
                sentence = span.sent

                # Check if the matched term is being used as a verb and skip if not
                is_actionable = any(token.pos_ == "VERB" for token in span)
                if not is_actionable:
                    continue

                sentence_text = sentence.text

                # Add (speaker, sentence) tuple only if it hasn't been added already
                # And check the context of the sentence to see if there are indicators for it being actionable
                if (not actionable_sentence_added and
                        any(indicator in sentence_text.lower() for indicator in context_indicators)):
                    actionable_sentences.add((current_speaker, sentence_text))
                    actionable_sentence_added = True

    return list(actionable_sentences)

# Output the detected actionable items to a text file
def outputActionableItems (transcript, filename):
    actionable_sentences = actionableItems(transcript)
    file = open(filename, "a")
    for speaker, sentence in actionable_sentences:
        file.write(f"- {speaker}: \"{sentence}\"\n")
    file.close()