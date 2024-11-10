# pip install -U spacy
# python -m spacy download en_core_web_sm

import spacy
from spacy.matcher import Matcher
import re
import docx2txt

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
        [{"LOWER": "finalize"}, {"IS_ALPHA": True, "OP": "?"}]
    ]

    matcher.add("ActionableItems", actionable_patterns)

    # Initialize variables
    actionable_sentences = set()  # Use a set to avoid duplicates
    current_speaker = None

    # Split the transcript into lines
    lines = transcript.splitlines()

    # Process each line in the transcript
    for i, line in enumerate(lines):
        # Detect timestamp line and skip if found
        timestamp_match = re.match(r"^\d+:\d+:\d+\.\d+\s-->\s\d+:\d+:\d+\.\d+$", line)
        if not timestamp_match:
            timestamp_match = re.match(r"^\d+:\d+:\d+\.\d+\s-->\s\d+:\d+:\d+\.\d+\s\s$", line)
        if timestamp_match:
            continue

        # Detect speaker line and capture full name of speaker
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
                if not actionable_sentence_added:
                    actionable_sentences.add((current_speaker, sentence_text))
                    actionable_sentence_added = True

    return list(actionable_sentences)

def outputActionableItems (filepath):
    transcript = docx2txt.process(filepath)
    actionable_sentences = actionableItems(transcript)
    print("Actionable Sentences Found:")
    for speaker, sentence in actionable_sentences:
        print(f"- {speaker}: \"{sentence}\"")