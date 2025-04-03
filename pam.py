# File Name: pam.py
# Authors: Javier Chung, Andy Dai, Antonio Lio, Jason Stuckless
# Description: Main file for PAM program with progress reporting functionality

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
from pam_deepseek8B import generate_minutes_doc

# Progress callback functionality
progress_callback = None


def set_progress_callback(callback_func):
    """
    Set a callback function to report progress

    Args:
        callback_func: Function with signature callback_func(progress_percent, status_message)
    """
    global progress_callback
    progress_callback = callback_func

    # Also set the progress callback for the GPT module
    #gpt.set_progress_callback(callback_func)


def report_progress(progress_percent, status_message):
    """
    Report progress to the registered callback if available

    Args:
        progress_percent: Progress as a percentage (0-100)
        status_message: Status message to display
    """
    if progress_callback:
        progress_callback(progress_percent, status_message)
    # Always print to console for logging
    print(f"Progress: {progress_percent}% - {status_message}")


# this function will run the summarization of our program
def summarize(filepath, model):
    try:
        # Report initial progress
        report_progress(5, "Detecting transcript format...")

        transcript_type = Transcript.detectTranscriptFormat(filepath)

        if transcript_type == 1:
            report_progress(10, "Processing standard transcript format...")
            transcript = docx2txt.process(filepath)
        elif transcript_type == 2:
            report_progress(10, "Converting Google Meet transcript format...")
            transcript = Transcript.convertMeet(filepath)
        elif transcript_type == 3:
            report_progress(10, "Converting Zoom transcript format...")
            transcript = Transcript.convertZoom(filepath)
        elif transcript_type == 4:
            report_progress(10, "Converting diarized transcript format...")
            transcript = Transcript.convertDiarization(filepath)
        elif transcript_type == 0:
            report_progress(100, "Invalid transcript format detected.")
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
            report_progress(15, "Initializing DeepSeek local model...")

            # Create a progress monitoring class for the DeepSeek local model
            class ProgressMonitor:
                def __init__(self):
                    self.last_stage = ""

                def update_step(self, step_name, step_progress=0):
                    # Map the step names to progress percentages
                    stage_mapping = {
                        "Initializing model and tokenizer": 15,
                        "Parsing transcript": 25,
                        "Extracting metadata": 35,
                        "Filtering dialogue": 50,
                        "Generating minutes": 75,
                        "Saving document": 95
                    }

                    self.last_stage = step_name
                    progress = stage_mapping.get(step_name, 15)
                    report_progress(progress, step_name)

                def update_progress(self, progress, items_processed=None, total_items=None):
                    # Calculate overall progress based on current stage
                    stage_mapping = {
                        "Initializing model and tokenizer": (15, 25),  # (start, end)
                        "Parsing transcript": (25, 35),
                        "Extracting metadata": (35, 50),
                        "Filtering dialogue": (50, 75),
                        "Generating minutes": (75, 95),
                        "Saving document": (95, 100)
                    }

                    if self.last_stage in stage_mapping:
                        start, end = stage_mapping[self.last_stage]
                        overall_progress = start + (end - start) * (progress / 100)

                        if items_processed is not None and total_items is not None:
                            msg = f"{self.last_stage}: {items_processed}/{total_items} items"
                        else:
                            msg = f"{self.last_stage}: {progress:.1f}% complete"

                        report_progress(int(overall_progress), msg)

                def complete(self):
                    report_progress(100, "Processing complete!")

            # Create monitor
            progress_monitor = ProgressMonitor()
            model_name = "DeepSeek-R1-Distill-Qwen-1.5B"

            # Patch the progress_tracker in pam_deepseek module if possible
            try:
                # Execute the local model with progress monitoring
                report_progress(15, "Starting DeepSeek local model processing...")
                # This is a workaround - the real implementation would modify the pam_deepseek module
                # to accept a progress_tracker parameter

                # Run the DeepSeek local model
                pam_deepseek.process_transcript(filepath, model_name, gpt.meetingNotesList)
                report_progress(95, "Finalizing meeting minutes...")

            except Exception as e:
                print(f"Error with DeepSeek local model: {str(e)}")
                report_progress(100, "Error with DeepSeek local model.")

        # DeepSeek API model for summarization
        elif model == 1:
            # Call the DeepSeek API implementation
            report_progress(15, "Initializing DeepSeek API...")
            # Set progress callback for GPT module to receive progress updates
            # gpt.set_progress_callback(progress_callback)
            gpt.deepseekAPI(filepath)
            report_progress(95, "Finalizing DeepSeek API results...")

        # OpenAI API model for summarization
        elif model == 2:
            # Call the OpenAI API implementation
            report_progress(15, "Initializing OpenAI API...")
            # Set progress callback for GPT module to receive progress updates
            # gpt.set_progress_callback(progress_callback)
            gpt.gptSummarization(filepath)
            report_progress(95, "Finalizing OpenAI results...")

        # Special handling for OpenAI model output (model 2)
        if model == 2:
            # Ensure we have enough sections in meetingNotesList
            # OpenAI's output might have 8 sections but we need to ensure proper formatting
            if len(gpt.meetingNotesList) < 8:
                report_progress(96, "Processing incomplete sections...")
                print("Warning: Incomplete sections in OpenAI output")
                # Pad with empty sections if needed
                while len(gpt.meetingNotesList) < 8:
                    gpt.meetingNotesList.append("No information provided")
        if model == 3:
            report_progress(15, "Initializing trained DeepSeek R1 8B model...")
            generate_minutes_doc(filepath)

        # Create file name for minutes document
        report_progress(97, "Creating minutes document...")
        basename = os.path.basename(filepath)
        base_filename = os.path.splitext(basename)[0]
        minutesFilename = base_filename + "_minutes.docx"

        # Generate minutes document from the meetingNotesList
        output_path = Minutes.generateMinutes(gpt.meetingNotesList, filepath, minutesFilename)
        report_progress(100, "Minutes successfully generated!")
        print(f"Minutes successfully generated at: {output_path}")

        return output_path

    except Exception as e:
        report_progress(100, f"Error: {str(e)}")
        print(f"Error in summarization process: {str(e)}")
        print("Traceback:", traceback.format_exc())
        report_progress(98, "Creating backup from terminal output...")
        create_backup_from_terminal_output(filepath)


def create_backup_from_terminal_output(filepath):
    """
    Create a basic text file with meeting notes from the terminal output
    as a fallback when the main minutes generation fails.
    """
    report_progress(99, "Creating backup file...")
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
        report_progress(100, f"Backup created at: {backup_path}")
        return backup_path

    except Exception as backup_error:
        print(f"Failed to create backup file: {str(backup_error)}")
        report_progress(100, f"Failed to create backup file: {str(backup_error)}")
        return None
