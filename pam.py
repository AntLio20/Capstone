# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Main file for PAM program

import Minutes
import Transcript
import GPT as gpt
import docx2txt
import pam_deepseek  # Import the DeepSeek R1 module
import traceback  # For detailed error information
import os  # For file operations


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
        gpt.meetingNotesList.clear() if hasattr(gpt, 'meetingNotesList') else setattr(gpt, 'meetingNotesList', [])

        # DeepSeek R1 model for summarization (local model)
        if model == 0:
            # Use the local DeepSeek R1 model from pam_deepseek.py
            pam_deepseek.process_transcript(filepath, gpt.meetingNotesList)

        # DeepSeek API model for summarization
        elif model == 1:
            # Call the DeepSeek API implementation
            gpt.deepseekAPI(filepath)

        # OpenAI API model for summarization
        elif model == 2:
            # Call the OpenAI API implementation
            gpt.gptSummarization(filepath)

        # Verify that meetingNotesList is populated before continuing
        if not gpt.meetingNotesList:
            print("Warning: No content generated in meetingNotesList. Check API response.")
            # Create a backup of the notes directly from the printed output
            create_backup_from_terminal_output(filepath)
            return

        # Create file name for minutes document
        minutesFilename = Transcript.extractFilenameDate(filepath) + "_minutes.docx"

        # Debugging output
        print("\nPreparing to generate minutes file:", minutesFilename)
        print(f"Number of sections in meetingNotesList: {len(gpt.meetingNotesList)}")

        try:
            # Generate minutes document from the meetingNotesList
            Minutes.generateMinutes(gpt.meetingNotesList, filepath, minutesFilename)
            print(f"Minutes successfully generated at: {minutesFilename}")
        except Exception as minutes_error:
            print(f"Error generating minutes file: {str(minutes_error)}")
            print("Traceback:", traceback.format_exc())
            create_backup_from_terminal_output(filepath)

    except Exception as e:
        print(f"Error in summarization process: {str(e)}")
        print("Traceback:", traceback.format_exc())


def create_backup_from_terminal_output(filepath):
    """
    Create a basic text file with meeting notes from the terminal output
    as a fallback when the main minutes generation fails.
    """
    try:
        # Create a simple text file as backup
        backup_filename = Transcript.extractFilenameDate(filepath) + "_meeting_notes.txt"

        with open(backup_filename, 'w') as backup_file:
            backup_file.write("MEETING NOTES (AUTO-GENERATED BACKUP)\n\n")

            # If we have content in meetingNotesList, use that
            if hasattr(gpt, 'meetingNotesList') and gpt.meetingNotesList:
                for i, section in enumerate(gpt.meetingNotesList):
                    if i < len(gpt.sectionHeadings):
                        backup_file.write(f"## {gpt.sectionHeadings[i]}\n")
                    else:
                        backup_file.write(f"## Section {i + 1}\n")
                    backup_file.write(f"{section}\n\n")
            else:
                backup_file.write("No content available. Please check the terminal output for meeting summary.\n")

        print(f"Backup notes created at: {backup_filename}")

    except Exception as backup_error:
        print(f"Failed to create backup file: {str(backup_error)}")