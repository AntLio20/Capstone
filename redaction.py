# Run these commands first to get redac to run:
# Install spacy: pip install spacy
# Download language model: python -m spacy download en_core_web_lg
# Install sklearn: pip install scikit-learn

from sklearn.cluster import KMeans
import spacy
import docx2txt

# Load spaCy model
nlp = spacy.load("en_core_web_lg")

# Define off-topic keywords
offTopicKeywords = ["quick aside", "off topic", "off the script", "off the logs", "not important", "readact"]

# Each text line is a node in the linked list
class SentenceNode:
    def __init__(self, text, isIgnored=False):
        self.text = text
        self.isIgnored = isIgnored
        self.next = None  # Pointer to the next node

# Build the linked list 
def buildLinkedList(transcriptLines):
    head = None
    prev = None
    for idx, line in enumerate(transcriptLines):
        # Idenitfy timestamps and speakers as ignored text
        isIgnored = (idx % 4 == 0) or (idx % 4 == 1)
        node = SentenceNode(line, isIgnored)
        if not head:
            head = node
        if prev:
            prev.next = node
        prev = node
    return head

# Function to cluster sentences within a block
def clusterSentences(sentencesBlock, nClusters):
    embeddings = [nlp(sentence).vector for sentence in sentencesBlock]
    kmeans = KMeans(n_clusters = nClusters, random_state=42)
    clusterLabels = kmeans.fit_predict(embeddings)
    return clusterLabels

# Strikethrough function for visualization, to indicate which text is removed later
def addStrikethrough(text):
    return f"[REDACTED: {text}]"


# Main redaction function
def redact(transcript):
    # Split the transcript into lines and build a linked list
    transcriptLines = transcript.splitlines()
    linkedList = buildLinkedList(transcriptLines)
    
    # Result string to store the redacted transcript
    redacted_transcript = ""

    # Iterate through linked list, redacting content as needed
    current = linkedList
    while current:
        if current.isIgnored:
            # If the line is to be ignored (timestamp or speaker name), add it as is
            if current.text.strip():
                redacted_transcript += current.text + "\n"
            current = current.next
            continue

        # Check if the current sentence contains an off-topic keyword
        if any(keyword in current.text for keyword in offTopicKeywords):
            # If it does, immediately apply strikethrough to this sentence
            redacted_transcript += addStrikethrough(current.text) + "\n"

            # Collect the immediate 3 sentences following the redaction indication
            initialContext = []
            tempNode = current.next
            count = 0
            while tempNode and count < 3:
                if not tempNode.isIgnored and tempNode.text.strip():
                    initialContext.append(tempNode.text)
                    count += 1
                tempNode = tempNode.next

            # Generate clusters to find the topic for redaction
            if initialContext:
                initialClusterLabels = clusterSentences(initialContext, 2)
                primaryOffTopicCluster = max(set(initialClusterLabels), key=list(initialClusterLabels).count)

            # Collect the following 10 sentences following the redaction indication
            tempNode = current.next
            count = 0
            remainingSentences = []
            nonIgnoredSentencesForClustering = []
            while tempNode and count < 10:
                if tempNode.text.strip():
                    remainingSentences.append(tempNode)
                    if not tempNode.isIgnored:
                        nonIgnoredSentencesForClustering.append(tempNode.text)
                        count += 1
                tempNode = tempNode.next

            # Generate clusters only for non-ignored sentences
            remainingClusterLabels = clusterSentences(nonIgnoredSentencesForClustering, 4)

            # Redact based on clusters
            for node in remainingSentences:
                if node.text.strip():
                    if node.isIgnored:
                        redacted_transcript += node.text + "\n"
                    else:
                        # Check if the cluster label for this sentence matches the primary off-topic cluster
                        nonIgnoredIndex = nonIgnoredSentencesForClustering.index(node.text) if node.text in nonIgnoredSentencesForClustering else -1
                        if nonIgnoredIndex != -1 and remainingClusterLabels[nonIgnoredIndex] == primaryOffTopicCluster:
                            redacted_transcript += addStrikethrough(node.text) + "\n"
                        else:
                            redacted_transcript += node.text + "\n"
            # Skip to the next sentence after the processed block
            current = tempNode
        
        else:
            # If no keyword is found, add the sentence as normal text
            if current.text.strip():
                redacted_transcript += current.text + "\n"

        # Move to the next node
        current = current.next

    return redacted_transcript