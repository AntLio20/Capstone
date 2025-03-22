# File Name: FileSystem.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Functionality for reading files in a directory

import os
import shutil
import docx2txt 
import re 


class FileSystem:

    def __init__(self, fileDirectory = "./MeetingNotes"):
        self.fileNames = []
        self.fileAmt = 0
        self.fileDirectory = fileDirectory
        self.sectionHeadings = ["Opening", "Present", "Absent", "Agenda Approval", "Previous Meeting Approval",
                   "Previous Meeting Summary", "Summary of Meeting", "Adjournment"]

    # this method searches for the amount of files wihtin the directory while populating a list with thier names
    def searchDirectory(self):

        # resetting the values
        self.fileNames = []
        self.fileAmt = 0

        # this views all the files and stores the path name of them in an array
        for f in os.listdir(self.fileDirectory):
            filepath = os.path.join(self.fileDirectory, f) # checking the files in the directory

            if (os.path.isfile(filepath) and f.endswith(".docx")): # finding .docx files and non corrupt files

                self.fileNames.append(f)
                self.fileAmt = self.fileAmt + 1

    # this method returns the file size
    def getSize(self, fileName):
        size = os.path.getsize(self.fileDirectory + "/" + fileName)
        return (str(size) + " bytes") 

    # this method move sthe file to a specified location
    def moveFile(self, fileName):
        destinationFilePath = os.path.join(self.fileDirectory, fileName)
        shutil.move( (fileName), destinationFilePath) 

    # this method returs a list of actionable items after opening a file
    def getActionableItemsList(self, fileName):
        actionableItemsList = []

        destinationFilePath = os.path.join(self.fileDirectory, fileName)

        try:
            # Try to process as a docx file first
            if fileName.endswith('.docx'):
                content = docx2txt.process(destinationFilePath)
                
                # Look for the "Action Items" section in the docx
                action_items_match = re.search(r"# Action Items\s+([\s\S]+?)(?=\s+#|$)", content)
                
                if action_items_match:
                    action_items_text = action_items_match.group(1)
                    # Extract bullet points
                    for line in action_items_text.split('\n'):
                        if line.strip().startswith('-'):
                            actionableItemsList.append(line.strip()[1:].strip())  # Remove the dash and trim
            else:
                # For text files
                with open(destinationFilePath, 'r') as f:
                    for line in f:
                        actionableItemsList.append(line.strip())
                        
        except Exception as e:
            print(f"Error reading actionable items from {fileName}: {str(e)}")
            # Return a default empty list on error
            
        return actionableItemsList

    def getHeadingsAndContent(self, fileName):
        try:
            destinationFilePath = os.path.join(self.fileDirectory, fileName)
            minutesDoc = docx2txt.process(destinationFilePath)  # reading the document
            
            # First check if the document has a transcript format with # headings
            transcript_format = re.findall(r"# ([^\n]+)\s+([\s\S]+?)(?=\s+#|$)", minutesDoc)
            
            if transcript_format and len(transcript_format) > 0:
                print(f"Detected transcript format with {len(transcript_format)} sections")
                
                # Create a mapping from transcript headings to expected section headings
                heading_map = {
                    "Date and Time": "Opening",
                    "Attendees": "Present",
                    "Key Discussion Topics": "Summary of Meeting",
                    "Decisions Made": "Previous Meeting Summary",
                    "Action Items": "Agenda Approval",
                    "Next Steps": "Adjournment"
                }
                
                # Convert transcript format to our required format
                formatted_sections = []
                
                for heading, content in transcript_format:
                    # Format the section heading to match what the app expects
                    formatted_heading = f"{heading}"
                    if heading in heading_map:
                        formatted_heading = f"{heading} ({heading_map[heading]})"
                        
                    # Format content - if it's a list with bullet points, keep the formatting
                    formatted_content = content.strip()
                    
                    formatted_sections.append((formatted_heading, formatted_content))
                
                return formatted_sections
            
            # If not in transcript format, try the original regex pattern for numbered sections
            headings = r"(\d+\.\s+[^\n]+)(.*?)(?=\n\d+\.\s|$)" 
            sections = re.findall(headings, minutesDoc, re.DOTALL)
            
            if sections and len(sections) > 0:
                print(f"Detected standard format with {len(sections)} sections")
                return sections
            
            # If we still don't have any sections, try a more general approach
            # Just look for any kind of section headers
            general_sections = re.findall(r"([A-Z][A-Za-z\s]+:)([^:]+)(?=\s*[A-Z][A-Za-z\s]+:|$)", minutesDoc)
            
            if general_sections and len(general_sections) > 0:
                print(f"Detected general format with {len(general_sections)} sections")
                return general_sections
            
            # If all parsing attempts fail, return the entire document as a single section
            print("No structured sections found, returning full document")
            return [("Document Content", minutesDoc)]
            
        except Exception as e:
            print(f"Error parsing document {fileName}: {str(e)}")
            # Return document as a single section with error message
            return [("Error Reading Document", f"There was an error parsing this document: {str(e)}")]


    def searchAudioDirectory(self):
        """Searches the MeetingRecordings directory for audio files"""
        import os

        self.audioDirectory = "MeetingRecordings"
        self.audioFileNames = []

        # Create directory if it doesn't exist
        if not os.path.exists(self.audioDirectory):
            os.makedirs(self.audioDirectory)
            return

        # Get all .wav files in the directory
        for file in os.listdir(self.audioDirectory):
            if file.endswith(".wav"):
                self.audioFileNames.append(file)

        # Sort files by creation date (newest first)
        self.audioFileNames.sort(key=lambda x: os.path.getctime(os.path.join(self.audioDirectory, x)), reverse=True)


    # Add this method to get the size of an audio file
    def getAudioSize(self, fileName):
        """Gets the size of an audio file in MB"""
        import os

        filePath = os.path.join(self.audioDirectory, fileName)
        sizeInBytes = os.path.getsize(filePath)
        sizeInMB = sizeInBytes / (1024 * 1024)

        return f"{sizeInMB:.2f} MB"