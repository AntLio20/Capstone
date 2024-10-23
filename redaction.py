# Run these commands first to get redac to run:
# Install spacy in the virtual environment: pip install spacy
# Download language model: python -m spacy download en_core_web_lg

import spacy
from collections import Counter, defaultdict
import Transcript
import docx2txt
from docx import Document
from docx.oxml import OxmlElement
from sklearn.cluster import KMeans

# Load language model
nlp = spacy.load("en_core_web_lg")

# Converts the document to a string
filepath = "trans.docx"
transcript = docx2txt.process(filepath)

# Extract and clean the transcript text
cleanedTranscript = Transcript.cleanTranscript(transcript, 0, 0)

# Process the cleaned text with spaCy
doc = nlp(cleanedTranscript)


# 1. Topic-Based Filtering (Named entities)

# Counting frequency of named entities
entityFreq = Counter([entity.text for entity in doc.ents])

# Set a threshold for named entities to be considered topics
topicEntities = [entity for entity, freq in entityFreq.items() if freq >= 2]
print("Identified main topics:", topicEntities)

# Clustering entities by semantic similarity
entityTexts = [entity.text for entity in doc.ents]
entityVectors = [nlp(entity.text).vector for entity in doc.ents]

# Using KMeans clustering to group similar entities 
n_clusters = 3  # Number of topic clusters
if len(entityVectors) > 0:
    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    kmeans.fit(entityVectors)
    labels = kmeans.labels_

    # Group entities based on their cluster labels
    clusters = defaultdict(list)
    for idx, label in enumerate(labels):
        clusters[label].append(entityTexts[idx])

    # Print clustered entities based on similarity
    print("\nEntities grouped by similarity:")
    for cluster_id, entities in clusters.items():
        print(f"Cluster {cluster_id}: {entities}")

# Create a new Document object to save the modified transcript
summarizedMeetingNotes = Document()

# Function to strikethrough text using Unicode
def addStrikethrough(paragraph, text):
    run = paragraph.add_run(text)
    # Apply strikethrough formatting using the underlying XML
    r = run._element
    rPr = r.get_or_add_rPr()
    strike = OxmlElement('w:strike')
    rPr.append(strike)

# Analyze off-topic by comparing each sentence to the clustered topics
for sentence in doc.sents:
    nounSentenceChunks = [chunk.text for chunk in sentence.noun_chunks]
    
    # Find intersection between sentence chunks and topic entities
    common_topics = set(nounSentenceChunks).intersection(topicEntities)
    common_clusters = any(set(nounSentenceChunks).intersection(set(cluster)) for cluster in clusters.values())
    
    # Add the sentence to the document
    paragraph = summarizedMeetingNotes.add_paragraph()
    
    if not common_topics and not common_clusters:
        # Apply strikethrough formatting if the sentence is off-topic
        addStrikethrough(paragraph, sentence.text)
    else:
        # Add normal text for on-topic sentences
        paragraph.add_run(sentence.text)

# Save the modified document with strikethroughs applied
summarizedMeetingNotes.save("test.docx")
print("Transcript saved as 'test.docx'")
