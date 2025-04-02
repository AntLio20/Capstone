# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Main file for PAM program

import Minutes
import Transcript
import GPT as gpt
import docx2txt
import pam_deepseek
import traceback
import os
import sys
import re
from docx import Document

# this function will run the summarization of our program
def summarize(filepath, model):
    try:
        transcript_type = Transcript.detectTranscriptFormat(filepath)

        if transcript_type == 1:
            transcript = docx2txt.process(filepath)
        elif transcript_type == 2:
            transcript = Transcript.convertMeet(filepath)
        elif transcript_type == 3:
            transcript = Transcript.convertZoom(filepath)
        elif transcript_type == 4:
            transcript = Transcript.convertDiarization(filepath)
        elif transcript_type == 0:
            print("Invalid Transcript Format")
            return  # Exit the function if transcript format is invalid

        # Reset the meeting notes list before processing
        if hasattr(gpt, 'meetingNotesList'):
            gpt.meetingNotesList.clear()
        else:
            gpt.meetingNotesList = []

        # DeepSeek R1 model for summarization (local model)
        if model == 0:
            # Use the local DeepSeek R1 model from pam_deepseek.py

            model_name = "DeepSeek-R1-Distill-Qwen-1.5B"
            pam_deepseek.process_transcript(filepath, model_name, gpt.meetingNotesList)

        # DeepSeek API model for summarization
        elif model == 1:
            # Call the DeepSeek API implementation
            gpt.deepseekAPI(filepath)

        # OpenAI API model for summarization
        elif model == 2:
            # Call the OpenAI API implementation
            gpt.gptSummarization(filepath)

        # Special handling for OpenAI model output (model 2)
        if model == 2:
            # Ensure we have enough sections in meetingNotesList
            # OpenAI's output might have 8 sections but we need to ensure proper formatting
            if len(gpt.meetingNotesList) < 8:
                print("Warning: Incomplete sections in OpenAI output")
                # Pad with empty sections if needed
                while len(gpt.meetingNotesList) < 8:
                    gpt.meetingNotesList.append("No information provided")
        if model == 3:
            model_name = "DeepSeek-R1-Distill-Llama-8B"
            pam_deepseek.process_transcript(filepath, model_name, gpt.meetingNotesList)

        # Create file name for minutes document
        basename = os.path.basename(filepath)
        base_filename = os.path.splitext(basename)[0]
        minutesFilename = base_filename + "_minutes.docx"

        # Generate minutes document from the meetingNotesList
        output_path = Minutes.generateMinutes(gpt.meetingNotesList, filepath, minutesFilename)
        print(f"Minutes successfully generated at: {output_path}")

    except Exception as e:
        print(f"Error in summarization process: {str(e)}")
        print("Traceback:", traceback.format_exc())
        create_backup_from_terminal_output(filepath)


def create_backup_from_terminal_output(filepath):
    """
    Create a basic text file with meeting notes from the terminal output
    as a fallback when the main minutes generation fails.
    """
    try:
        # Create a simple text file as backup
        basename = os.path.basename(filepath)
        base_filename = os.path.splitext(basename)[0]
        backup_filename = base_filename + "_backup_notes.txt"

        os.makedirs("MeetingNotes", exist_ok=True)
        backup_path = os.path.join("MeetingNotes", backup_filename)

        with open(backup_path, 'w') as backup_file:
            backup_file.write("MEETING NOTES (AUTO-GENERATED BACKUP)\n\n")

            # If we have content in meetingNotesList, use that
            if hasattr(gpt, 'meetingNotesList') and gpt.meetingNotesList:
                section_titles = [
                    "Opening Information",
                    "Present Members",
                    "Absent Members",
                    "Agenda Approval",
                    "Previous Meeting Minutes Approval",
                    "Summary of Last Meeting",
                    "Meeting Summary",
                    "Adjournment"
                ]

                for i, section in enumerate(gpt.meetingNotesList):
                    if i < len(section_titles):
                        backup_file.write(f"## {section_titles[i]}\n")
                    else:
                        backup_file.write(f"## Section {i + 1}\n")
                    backup_file.write(f"{section}\n\n")
            else:
                backup_file.write("No content available. Please check the terminal output for meeting summary.\n")

        print(f"Backup notes created at: {backup_path}")

    except Exception as backup_error:
        print(f"Failed to create backup file: {str(backup_error)}")