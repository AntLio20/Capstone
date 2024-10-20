# Run these commands first to get the library to run:
# Install spacy in the virtual environment: pip install spacy
# Download language model: python -m spacy download en_core_web_sm

import spacy
from collections import Counter
import Transcript

# Load language model
nlp = spacy.load("en_core_web_sm")

# Extract and clean the transcript text
cleanedText = Transcript.cleanTranscript(Transcript.getText("meeting.docx"), 0, 0)

# Process the cleaned text with spaCy
doc = nlp(cleanedText)

# 1. Topic-Based Filtering (Named entities)

# Counting frequency of named entities
entityFreq = Counter([entity.text for entity in doc.ents])

# Set a threshold for named entities to be cosidered topics (NEED TO ADJUST LATER)
topicEntities = [entity for entity, freq in entityFreq.items() if freq >= 2]
print("Identified main topics:", topicEntities)

# Analyze off-topic by comparing each sentence to the main topics
offTopicSentences = []
for sentence in doc.sents:
    nounSentenceChunks = [chunk.text for chunk in sentence.noun_chunks]
    common = set(nounSentenceChunks).intersection(topicEntities)
    if not common:
        offTopicSentences.append(sentence.text)