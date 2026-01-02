"""
Voice input module that uses the external 'listen' command for recording and transcription.
"""

import logging
import subprocess
import threading
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class VoiceInput:
    """Manages voice input by calling the external 'listen' command."""

    def __init__(
        self,
        listen_command_path: str = "/home/rseward/bin/listen.sh",
        on_complete: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the VoiceInput.

        Args:
            listen_command_path: Path to the listen command executable
            on_complete: Callback function called with transcribed text when done
        """
        self.listen_command_path = listen_command_path
        self.on_complete = on_complete
        self.process: Optional[subprocess.Popen] = None
        self.is_recording = False

    def start_recording(self) -> None:
        """Start voice recording by launching the listen command in a background thread."""
        if self.is_recording:
            logger.warning("Recording already in progress")
            return

        logger.info("Starting voice recording via external listen command")
        self.is_recording = True

        # Run the listen command in a separate thread
        thread = threading.Thread(target=self._run_listen_command, daemon=True)
        thread.start()

    def _run_listen_command(self) -> None:
        """Run the listen command and capture its output (runs in separate thread)."""
        try:
            logger.info(f"Executing: {self.listen_command_path}")

            # Run the listen command and capture stdout
            self.process = subprocess.Popen(
                [self.listen_command_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for the process to complete and get output
            stdout, stderr = self.process.communicate()

            if stderr:
                logger.debug(f"Listen command stderr: {stderr}")

            transcribed_text = stdout.strip()
            logger.info(f"Transcription received: {transcribed_text}")

            # Call the completion callback with the transcribed text
            if self.on_complete:
                self.on_complete(transcribed_text)

        except Exception as e:
            logger.error(f"Error running listen command: {e}")
            if self.on_complete:
                self.on_complete("")

        finally:
            self.is_recording = False
            self.process = None

    def stop_recording(self) -> None:
        """Stop the recording process if it's running."""
        if self.process and self.process.poll() is None:
            logger.info("Terminating listen command process")
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                logger.warning("Process didn't terminate, killing it")
                self.process.kill()
            except Exception as e:
                logger.error(f"Error stopping process: {e}")

        self.is_recording = False
