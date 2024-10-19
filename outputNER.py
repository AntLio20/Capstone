# pip install -U spacy
# python -m spacy download en_core_web_lg
import os
import spacy
from spacy import displacy
import Transcript

# import transcript file and remove timestamps and speaker from text
transcript = Transcript.cleanTranscript(Transcript.getText("meeting.docx"), 0, 0)

# prepare spacy pipeline and assign it the transcript file to analyse
nlp = spacy.load("en_core_web_lg")
doc = nlp(transcript)

# remove files if they already exist
if os.path.isfile("transcript.html"):
    os.remove("transcript.html")
if os.path.isfile("transcriptDependencies.html"):
    os.remove("transcriptDependencies.html")

# create HTML document of transcript with NER items highlighted and labelled
# options = {"ents": ["NOUN"]} , options=options
# (WIP: trying to show more highlighted types on NER visualization)
html = displacy.render(doc, style="ent", page=True)
f = open("transcript.html", "x")
f.write(html)

# create HTML document of transcript with sentence dependencies
sentences = list(doc.sents)
html2 = displacy.render(sentences, style="dep", page=True)
f2 = open("transcriptDependencies.html", "x")
f2.write(html2)