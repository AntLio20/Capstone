from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
import sys
import os
import random
import time

# Import the modules we need to patch
import pam


# Thread class to handle summarization in the background with animated progress
class SummarizationThread(QThread):
    """Enhanced thread class that shows gradual progress for API-based models"""
    # Define signals to communicate with the UI
    progressUpdated = pyqtSignal(int)
    statusUpdated = pyqtSignal(str)
    summarizationComplete = pyqtSignal(str)
    summarizationError = pyqtSignal(str)

    def __init__(self, filepath, model_index):
        super().__init__()
        self.filepath = filepath
        self.model_index = model_index
        self.is_running = True
        self.current_progress = 0
        self.progress_timer = None

        # Animation tracking variables
        self.simulation_progress = 0
        self.last_reported_progress = 0
        self.last_update_time = 0
        self.api_started = False

    def run(self):
        try:
            # Initial status update
            self.statusUpdated.emit("Initializing summarization...")
            self.progressUpdated.emit(5)

            # Set up the progress callback for pam module
            pam.set_progress_callback(self.handle_progress_update)

            # For API models, prepare animation but don't start it yet
            if self.model_index in [1, 2]:  # DeepSeek API or OpenAI API
                self.prepare_progress_simulation(self.model_index)

            # Call the summarize function
            output_path = pam.summarize(self.filepath, self.model_index)

            # Stop the timer if it's running
            if self.progress_timer and self.progress_timer.isActive():
                self.progress_timer.stop()

            # Final progress update and completion signal
            self.progressUpdated.emit(100)
            self.statusUpdated.emit("Summarization complete!")

            # Get the output filename if not provided
            if not output_path:
                basename = os.path.basename(self.filepath)
                base_filename = os.path.splitext(basename)[0]
                output_path = os.path.join("MeetingNotes", base_filename + "_minutes.docx")

            self.summarizationComplete.emit(output_path)

        except Exception as e:
            if self.progress_timer and self.progress_timer.isActive():
                self.progress_timer.stop()
            self.summarizationError.emit(f"Error during summarization: {str(e)}")

    def handle_progress_update(self, progress_percent, status_message):
        """Callback function to receive progress updates from the pam module"""
        self.current_progress = progress_percent
        self.progressUpdated.emit(progress_percent)
        self.statusUpdated.emit(status_message)

        # For OpenAI API, always start emergency animation when we hit 20%
        if self.model_index == 2 and progress_percent == 20 and not hasattr(self, 'animation_running'):
            self.force_progress_animation()

        # Stop the animation when we get a high progress value
        # Add additional check to ensure animation is stopped
        if progress_percent >= 90 and hasattr(self, 'animation_running'):
            self.animation_running = False

    def start_progress_simulation(self):
        """Start the timer for progress simulation"""

        # Create a simple recurring timer that just increments the progress
        self.simulation_progress = 20
        self.simulation_active = True

        def increment_progress():
            self.simulation_progress += 1
            if self.simulation_progress <= 90:
                self.progressUpdated.emit(self.simulation_progress)
                self.statusUpdated.emit(f"Processing API request... {self.simulation_progress}%")
                # Return True to keep timer active
                return True
            else:
                return False  # Stop timer when reaching 90%

        # Use QTimer.singleShot with recursive calls instead of timeout signal
        def create_timer():
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(2000, lambda: increment_progress() and create_timer())

        # Start the first timer
        create_timer()

    def update_simulated_progress(self):
        """Update the progress bar with a simulated value during API calls"""
        # Stop if the thread is no longer running
        if not self.is_running:
            if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
                self.progress_timer.stop()
            return

        # Stop if real progress has caught up
        if self.current_progress >= 90:
            if hasattr(self, 'progress_timer') and self.progress_timer.isActive():
                self.progress_timer.stop()
            return

        # If real progress has jumped ahead, use that instead
        if self.current_progress > self.simulation_progress + 5:
            self.simulation_progress = self.current_progress
            self.progressUpdated.emit(self.current_progress)
            return

        # Update the progress by 1% each time
        if self.simulation_progress < self.target_progress:
            self.simulation_progress += 1

            # Find appropriate status message based on current progress
            for threshold, message in self.progress_stages:
                if self.simulation_progress <= threshold:
                    self.statusUpdated.emit(message)
                    break

            # Update UI
            self.progressUpdated.emit(int(self.simulation_progress))

    def force_progress_animation(self):
        """Emergency progress animation function with proper stopping mechanism"""
        # Create a flag to control the animation thread
        self.animation_running = True

        # Create a simple direct approach to update the progress
        import threading
        import time

        def progress_updater():
            # Adjust the start and end points based on the model
            progress = self.start_progress

            # Add a stop condition directly in the thread
            while progress < 90 and self.is_running and self.animation_running:
                time.sleep(2)  # Wait 2 seconds

                # Check current real progress frequently
                if self.current_progress >= 90:
                    self.animation_running = False
                    break

                progress += 1
                # These are thread-safe signals
                self.progressUpdated.emit(progress)
                self.statusUpdated.emit(f"Processing API request... {progress}%")

        # Start a dedicated thread for this
        self.animation_thread = threading.Thread(target=progress_updater)
        self.animation_thread.daemon = True  # Thread will exit when main thread exits
        self.animation_thread.start()

    def prepare_progress_simulation(self, model_index):
        """Prepare the progress simulation parameters based on model type"""
        # Determine interval and progress ranges for API models only
        if model_index in [1, 2]:  # DeepSeek API or OpenAI API
            if model_index == 1:  # DeepSeek API
                self.interval = 300  # milliseconds between updates (faster)
                self.start_progress = 30  # Start at 30% for DeepSeek API
                self.target_progress = 89
                self.progress_increment = 0.4  # slightly faster progress

                # Simulate chunk processing stages for DeepSeek API
                self.progress_points = [
                    (40, "Processing transcript with DeepSeek API..."),
                    (55, "Analyzing conversation structure..."),
                    (70, "Extracting key points and action items..."),
                    (80, "Organizing meeting sections..."),
                    (89, "Awaiting API response...")
                ]
            else:  # OpenAI API
                self.interval = 250  # milliseconds between updates (faster)
                self.start_progress = 20  # Start at 20% for OpenAI API
                self.target_progress = 89
                self.progress_increment = 0.3  # slow but steady progress

                # Simulate chunk processing stages for OpenAI API
                self.progress_points = [
                    (35, "Waiting for OpenAI API response..."),
                    (50, "AI processing transcript data..."),
                    (65, "Extracting meeting information..."),
                    (75, "Summarizing discussion points..."),
                    (85, "Identifying action items..."),
                    (89, "Awaiting final response...")
                ]

            # For API models, add an explicit progress animation
            # Only add animation if it hasn't been started already
            if not hasattr(self, 'animation_running'):
                self.force_progress_animation()

        else:
            # For non-API models, reset these attributes to prevent unexpected behavior
            self.interval = 300
            self.start_progress = 5
            self.target_progress = 95
            self.progress_points = [
                (20, "Processing transcript..."),
                (50, "Analyzing content..."),
                (75, "Generating summary..."),
                (95, "Finalizing document...")
            ]

        # Initialize the current simulation progress to match current real progress
        self.simulation_progress = self.start_progress

    def start_progress_simulation(self):
        """Start the timer for progress simulation"""
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_simulated_progress)
        self.last_update_time = time.time()
        self.progress_timer.start(self.interval)

    def update_simulated_progress(self):
        """Update the progress bar with a simulated value during API calls"""
        # Stop if we're no longer running or if the real progress has jumped ahead
        if not self.is_running or self.current_progress >= 90:
            if self.progress_timer and self.progress_timer.isActive():
                self.progress_timer.stop()
            return

        # If real progress has jumped ahead, use that instead
        if self.current_progress > self.simulation_progress + 10:
            if self.progress_timer and self.progress_timer.isActive():
                self.progress_timer.stop()
            return

        # Calculate elapsed time since last update to ensure steady progress
        now = time.time()
        elapsed = now - self.last_update_time
        self.last_update_time = now

        # Use a non-linear progress simulation to make it feel more natural
        # Slow down as we get closer to completion
        remaining = self.target_progress - self.simulation_progress
        if remaining < 10:
            increment = self.progress_increment * 0.3 * elapsed  # very slow near completion
        elif remaining < 20:
            increment = self.progress_increment * 0.5 * elapsed  # slow down near completion
        elif remaining < 40:
            increment = self.progress_increment * 0.7 * elapsed  # slightly slower
        else:
            increment = self.progress_increment * elapsed  # normal speed

        # Add a tiny bit of randomness
        increment += random.uniform(-0.05, 0.1)

        # Update simulated progress
        self.simulation_progress += increment
        self.simulation_progress = min(self.simulation_progress, self.target_progress)

        # Find the appropriate status message
        status_message = "Processing transcript data..."
        for threshold, message in self.progress_points:
            if self.simulation_progress <= threshold:
                status_message = message
                break

        # Update UI with integer progress value (to avoid too many updates)
        progress_value = int(self.simulation_progress)
        if progress_value != self.last_reported_progress:
            self.progressUpdated.emit(progress_value)
            self.statusUpdated.emit(status_message)
            self.last_reported_progress = progress_value

    def stop(self):
        """Stop the thread and timer"""
        self.is_running = False
        if self.progress_timer and self.progress_timer.isActive():
            self.progress_timer.stop()


# Function to modify SummarizationPage class
def integrate_progress_bar(summarization_page):
    """
    Integrates progress bar functionality into the SummarizationPage class

    Args:
        summarization_page: Instance of SummarizationPage to modify
    """
    # Add progress bar
    summarization_page.progressBar = QProgressBar(summarization_page)
    summarization_page.progressBar.setMinimum(0)
    summarization_page.progressBar.setMaximum(100)
    summarization_page.progressBar.setValue(0)
    summarization_page.progressBar.setTextVisible(True)
    summarization_page.progressBar.setFixedHeight(30)
    summarization_page.progressBar.setFixedWidth(400)  # Match width
    summarization_page.progressBar.setStyleSheet("""
        QProgressBar {
            border: 2px solid grey;
            border-radius: 5px;
            background-color: #F5F5F5;
            text-align: center;
            font-size: 14px;
        }

        QProgressBar::chunk {
            background-color: #4682B4;
            width: 10px;
            margin: 0.5px;
        }
    """)

    # Create status label
    summarization_page.statusLabel = QLabel("Ready to summarize", summarization_page)
    summarization_page.statusLabel.setStyleSheet("""
        font-size: 16px;
        color: #333333;
        margin-top: 5px;
    """)
    summarization_page.statusLabel.setAlignment(Qt.AlignCenter)
    summarization_page.statusLabel.setFixedWidth(400)  # Match width

    # Initially hide both until summarization starts
    summarization_page.progressBar.setVisible(False)
    summarization_page.statusLabel.setVisible(False)

    # Add to layout - find a good place to insert the progress bar
    layout = summarization_page.layout()

    # Find the index where we should insert the progress bar - look for button layout
    button_idx = None

    # Method 1: Try to find the button layout directly
    for i in range(layout.count()):
        item = layout.itemAt(i)
        if item and hasattr(item, 'layout') and isinstance(item.layout(), QHBoxLayout):
            # Check if this layout contains buttons
            button_layout = item.layout()
            for j in range(button_layout.count()):
                widget = button_layout.itemAt(j).widget()
                if isinstance(widget, QPushButton):
                    button_idx = i
                    break
            if button_idx is not None:
                break

    # Method the 2: If button layout not found, look for the buttons directly
    if button_idx is None:
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and hasattr(widget, 'text'):
                if "Summarize" in widget.text() or "Browse" in widget.text():
                    button_idx = i
                    break

    # Method 3: If all else fails, find the dropdown
    if button_idx is None:
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if hasattr(widget, 'currentIndex'):  # QComboBox has this method
                # Insert after the dropdown
                button_idx = i + 1
                break

    # Insert progress elements
    if button_idx is not None:
        # Insert before the buttons
        layout.insertWidget(button_idx, summarization_page.statusLabel, alignment=Qt.AlignCenter)
        layout.insertWidget(button_idx + 1, summarization_page.progressBar, alignment=Qt.AlignCenter)
    else:
        # Fallback - add them at the end
        layout.addWidget(summarization_page.statusLabel, alignment=Qt.AlignCenter)
        layout.addWidget(summarization_page.progressBar, alignment=Qt.AlignCenter)

    # Define handler methods
    def handle_summarization_complete(output_path):
        """Handle successful summarization"""
        # Re-enable UI controls
        summarization_page.dropdown.setEnabled(True)
        summarization_page.browseButton.setEnabled(True)
        summarization_page.summarizeButton.setEnabled(True)

        # Show success message
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Summarization complete!\nFile saved to: {output_path}")
        msg.setWindowTitle("Success")
        msg.exec_()

        # Update the main page to reflect the new file
        mainPage = summarization_page.stack.widget(1)
        mainPage.updateDocuments()

        # Navigate back to main page
        summarization_page.stack.setCurrentIndex(1)

    def handle_summarization_error(error_message):
        """Handle summarization error"""
        # Re-enable UI controls
        summarization_page.dropdown.setEnabled(True)
        summarization_page.browseButton.setEnabled(True)
        summarization_page.summarizeButton.setEnabled(True)

        # Reset progress bar
        summarization_page.progressBar.setValue(0)
        summarization_page.statusLabel.setText("Summarization failed")

        # Show error message
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(error_message)
        msg.setWindowTitle("Summarization Error")
        msg.exec_()

    # Store the original summarize method
    original_summarize = summarization_page.summarize

    # Define the new enhanced summarize method
    def enhanced_summarize(filename):
        # Don't proceed if filename is just the placeholder
        if filename == "Drop File Here":
            # Show a message to the user
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Please select a file to summarize")
            msg.setWindowTitle("No File Selected")
            msg.exec_()
            return

        # Make progress bar and status label visible
        summarization_page.progressBar.setVisible(True)
        summarization_page.statusLabel.setVisible(True)
        summarization_page.progressBar.setValue(0)
        summarization_page.statusLabel.setText("Starting summarization...")

        # Disable UI controls during processing
        summarization_page.dropdown.setEnabled(False)
        summarization_page.browseButton.setEnabled(False)
        summarization_page.summarizeButton.setEnabled(False)

        # Get the model index from the dropdown
        model_index = summarization_page.dropdown.currentIndex()

        # Create and start the thread
        summarization_page.summarization_thread = SummarizationThread(filename, model_index)

        # Connect signals
        summarization_page.summarization_thread.progressUpdated.connect(summarization_page.progressBar.setValue)
        summarization_page.summarization_thread.statusUpdated.connect(summarization_page.statusLabel.setText)
        summarization_page.summarization_thread.summarizationComplete.connect(handle_summarization_complete)
        summarization_page.summarization_thread.summarizationError.connect(handle_summarization_error)

        # Start the thread
        summarization_page.summarization_thread.start()

    # Replace the original method
    summarization_page.summarize = enhanced_summarize
    summarization_page.handle_summarization_complete = handle_summarization_complete
    summarization_page.handle_summarization_error = handle_summarization_error

    # Also override the navigateHome method to potentially stop the thread
    original_navigate_home = summarization_page.navigateHome

    def enhanced_navigate_home():
        # Stop the summarization thread if it's running
        if hasattr(summarization_page,
                   'summarization_thread') and summarization_page.summarization_thread and summarization_page.summarization_thread.isRunning():
            summarization_page.summarization_thread.stop()
            summarization_page.summarization_thread.wait()

        # Re-enable UI controls
        summarization_page.dropdown.setEnabled(True)
        summarization_page.browseButton.setEnabled(True)
        summarization_page.summarizeButton.setEnabled(True)

        # Hide progress elements
        summarization_page.progressBar.setVisible(False)
        summarization_page.statusLabel.setVisible(False)

        # Call the original method
        original_navigate_home()

    # Replace the navigate home method
    summarization_page.navigateHome = enhanced_navigate_home