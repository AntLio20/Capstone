import re
import spacy
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy model with NER capabilities
nlp = spacy.load("en_core_web_lg")

# Introduction phrases for fuzzy logic
intro_phrases = [
    "Hi, my name is",
    "Hello, my name is",
    "Hey, my name is",
    "Hi, I'm",
    "Hello, I'm",
    "Hey, I'm",
    "I am",
    "I'm",
    "My name is",
    "This is",
    "It's me,",
    "You can call me",
    "I go by",
    "People call me",
    "Let me introduce myself, I am",
    "Allow me to introduce myself, I'm",
    "Nice to meet you, I'm",
    "Pleasure to meet you, my name is",
    "Hey everyone, I'm",
    "Hi there, my name is",
    "Hello everyone, my name is",
    "Hey folks, I’m",
    "For those who don’t know me, I’m",
    "If you haven’t met me before, I’m",
    "By the way, I’m",
    "You might know me as",
    "Just so you know, I’m",
    "Let me quickly introduce myself, I’m",
    "I just wanted to say, I’m",
    "Hi all, I’m",
    "Hello all, my name is",
    "Hey team, my name is"
]

# Pre-compute embeddings for fuzzy comparison
intro_embeddings = [nlp(phrase).vector for phrase in intro_phrases]

# First-person pronoun check
FIRST_PERSON_PRONOUNS = ["i", "i'm", "im", "my", "me", "mine", "is"]

def contains_first_person(sentence):
    tokens = sentence.lower().split()
    return any(p in tokens for p in FIRST_PERSON_PRONOUNS)

# Sentence node for linked list
class SentenceNode:
    def __init__(self, text, isIgnored=False):
        self.text = text
        self.isIgnored = isIgnored
        self.next = None

def buildLinkedList(transcriptLines):
    head = None
    prev = None
    for line in transcriptLines:
        line = line.strip()
        isIgnored = False

        if re.match(r"\d+\.\d+\s+-->\s+\d+\.\d+", line):
            isIgnored = True
        elif re.match(r"SPEAKER_\d+", line):
            isIgnored = True

        node = SentenceNode(line, isIgnored)
        if not head:
            head = node
        if prev:
            prev.next = node
        prev = node
    return head

def isIntroduction(sentence, threshold=0.7):
    if not sentence.strip():
        return False, 0.0
    sentence_embedding = nlp(sentence).vector.reshape(1, -1)
    similarities = cosine_similarity(sentence_embedding, np.array(intro_embeddings))
    max_similarity = np.max(similarities)
    return max_similarity >= threshold, max_similarity

def extract_name_with_ner(sentence):
    doc = nlp(sentence)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_speaker_labels(transcript):
    speaker_pattern = re.findall(r"SPEAKER_\d+", transcript)
    unique_speakers = sorted(set(speaker_pattern), key=lambda x: int(x.split("_")[1]))
    return unique_speakers

def update_speaker_list(speaker_number, name, speaker_identifiers):
    if 0 <= speaker_number < len(speaker_identifiers):
        speaker_identifiers[speaker_number] = name

# Main pipeline function
def identify_and_replace_speakers(transcript: str) -> str:
    transcriptLines = transcript.splitlines()
    unique_speakers = extract_speaker_labels(transcript)
    speaker_identifiers = [int(spk.split("_")[1]) for spk in unique_speakers]

    linkedList = buildLinkedList(transcriptLines)
    current = linkedList
    current_speaker = None
    processed_lines = []

    while current:
        line = current.text.strip()

        # Update current speaker
        if re.match(r"SPEAKER_\d+", line):
            current_speaker = int(line.split("_")[1])
            speaker_label = speaker_identifiers[current_speaker]
            label_text = str(speaker_label) if isinstance(speaker_label, str) else f"SPEAKER_{speaker_label:02d}"
            processed_lines.append(label_text)
            current = current.next
            continue

        # Skip non-analyzable lines
        if current.isIgnored or not line or current_speaker is None:
            processed_lines.append(current.text)
            current = current.next
            continue

        # Check for intro
        is_intro, certainty = isIntroduction(line)
        if is_intro and contains_first_person(line):
            name = extract_name_with_ner(line)
            if name and isinstance(speaker_identifiers[current_speaker], int):
                update_speaker_list(current_speaker, name, speaker_identifiers)

        processed_lines.append(current.text)
        current = current.next

    # Replace speaker labels in the final output using updated identifiers
    final_output = []
    for line in processed_lines:
        match = re.match(r"SPEAKER_(\d+)", line)
        if match:
            speaker_num = int(match.group(1))
            identifier = speaker_identifiers[speaker_num]
            final_output.append(str(identifier))
        else:
            final_output.append(line)

    return "\n".join(final_output)