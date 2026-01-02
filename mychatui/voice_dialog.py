"""
Voice input dialog window for recording and transcribing audio.
"""

import logging
import threading
from typing import Optional

import customtkinter as ctk

from mychatui.voice_recorder import VoiceRecorder

logger = logging.getLogger(__name__)


class VoiceDialog(ctk.CTkToplevel):
    """Popup dialog for voice recording and transcription."""

    def __init__(
        self, parent, on_complete: Optional[callable] = None, model_size: str = "base"
    ):
        """
        Initialize the voice dialog.

        Args:
            parent: Parent window
            on_complete: Callback function called with transcribed text when done
            model_size: Whisper model size to use
        """
        super().__init__(parent)

        self.parent_window = parent
        self.on_complete = on_complete
        self.recorder: Optional[VoiceRecorder] = None
        self.model_size = model_size
        self.transcribed_text = ""

        # Window configuration
        self.title("Voice Input")
        self.geometry("400x300")
        self.resizable(False, False)

        # Center the window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Set appearance
        ctk.set_appearance_mode("dark")

        # Create UI
        self.create_widgets()

        # Initialize recorder in background
        self.status_label.configure(text="Loading model...")
        self.update()
        threading.Thread(target=self.initialize_recorder, daemon=True).start()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self) -> None:
        """Create the dialog UI components."""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame, text="Initializing...", font=("Arial", 14)
        )
        self.status_label.pack(pady=10)

        # Stop button
        self.stop_button = ctk.CTkButton(
            main_frame,
            text="⏹ Stop Recording",
            command=self.stop_recording,
            width=200,
            height=50,
            font=("Arial", 16, "bold"),
            state="disabled",
            fg_color="#dc3545",
            hover_color="#c82333",
        )
        self.stop_button.pack(pady=20)

        # Transcription display
        self.transcription_frame = ctk.CTkScrollableFrame(
            main_frame, width=360, height=120
        )
        self.transcription_frame.pack(pady=10, fill="both", expand=True)

        self.transcription_label = ctk.CTkLabel(
            self.transcription_frame,
            text="",
            wraplength=340,
            justify="left",
            font=("Arial", 12),
        )
        self.transcription_label.pack(pady=5)

    def initialize_recorder(self) -> None:
        """Initialize the voice recorder and start recording."""
        try:
            logger.info("Initializing voice recorder")
            self.recorder = VoiceRecorder(
                model_size=self.model_size,
                use_cuda=False,
                on_transcription=self.on_transcription_update,
            )
            self.recorder.initialize_model()

            # Start recording immediately after initialization
            self.after(0, self.start_recording)

        except Exception as e:
            logger.error(f"Failed to initialize recorder: {e}")
            error_msg = f"Initialization failed: {e}"
            self.after(0, lambda msg=error_msg: self.show_error(msg))

    def start_recording(self) -> None:
        """Start the recording process."""
        try:
            logger.info("Starting voice recording")
            self.status_label.configure(text="🎤 Recording... Speak now")
            self.stop_button.configure(state="normal")
            self.transcription_label.configure(text="")

            self.recorder.start_recording()

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self.show_error(f"Recording failed: {e}")

    def stop_recording(self) -> None:
        """Stop recording and return the transcription."""
        logger.info("Stop recording button clicked")
        self.status_label.configure(text="Processing...")
        self.stop_button.configure(state="disabled")

        # Stop recording in background thread
        threading.Thread(target=self._stop_and_complete, daemon=True).start()

    def _stop_and_complete(self) -> None:
        """Stop recording and complete the dialog (runs in separate thread)."""
        try:
            if self.recorder:
                self.transcribed_text = self.recorder.stop_recording()
                self.recorder.cleanup()

            logger.info(f"Transcription complete: {self.transcribed_text}")

            # Call the completion callback with the transcribed text
            if self.on_complete:
                self.after(0, lambda: self.on_complete(self.transcribed_text))

            # Close the dialog
            self.after(100, self.destroy)

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            error_msg = f"Error: {e}"
            self.after(0, lambda msg=error_msg: self.show_error(msg))

    def on_transcription_update(self, text: str) -> None:
        """
        Called when new transcription text is available.

        Args:
            text: New transcribed text segment
        """
        logger.debug(f"Transcription update: {text}")

        # Update the display with accumulated text
        def update_display():
            current_text = self.recorder.get_transcription() if self.recorder else ""
            self.transcription_label.configure(text=current_text)

        self.after(0, update_display)

    def show_error(self, message: str) -> None:
        """Display an error message."""
        logger.error(f"Voice dialog error: {message}")
        self.status_label.configure(text=f"Error: {message}")
        self.stop_button.configure(state="disabled")

        # Auto-close after showing error for a moment
        self.after(3000, self.destroy)

    def on_closing(self) -> None:
        """Handle window closing event."""
        logger.info("Voice dialog closing")

        if self.recorder:
            try:
                self.recorder.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up recorder: {e}")

        self.destroy()
