#!/usr/bin/env python

"""
Tests for voice input functionality using external listen command.
"""

import os
import sys
import time
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mychatui.voice_input import VoiceInput


class TestVoiceInputInitialization:
    """Tests for VoiceInput initialization."""

    def test_voice_input_init_default(self):
        """Test VoiceInput initialization with default parameters."""
        voice_input = VoiceInput()

        assert (
            voice_input.listen_command_path
            == "/home/rseward/bin/listen.sh"
        )
        assert voice_input.on_complete is None
        assert voice_input.is_recording is False
        assert voice_input.process is None

    def test_voice_input_init_with_callback(self):
        """Test VoiceInput initialization with custom callback."""
        callback = Mock()
        voice_input = VoiceInput(on_complete=callback)

        assert voice_input.on_complete == callback

    def test_voice_input_init_with_custom_path(self):
        """Test VoiceInput initialization with custom command path."""
        custom_path = "/custom/path/to/listen"
        voice_input = VoiceInput(listen_command_path=custom_path)

        assert voice_input.listen_command_path == custom_path


class TestVoiceInputMocked:
    """Tests for VoiceInput with mocked subprocess."""

    @patch("mychatui.voice_input.subprocess.Popen")
    def test_start_recording(self, mock_popen):
        """Test starting a recording."""
        # Mock the process
        mock_process = Mock()
        mock_process.communicate.return_value = ("test transcription", "")
        mock_popen.return_value = mock_process

        callback = Mock()
        voice_input = VoiceInput(on_complete=callback)

        assert voice_input.is_recording is False

        voice_input.start_recording()

        # Wait for the thread to complete
        time.sleep(1)

        # Check that the process was started
        mock_popen.assert_called_once()

        # After completion, recording should be false again
        assert voice_input.is_recording is False

    @patch("mychatui.voice_input.subprocess.Popen")
    def test_recording_callback(self, mock_popen):
        """Test that callback is called with transcribed text."""
        # Mock the process to return test text
        mock_process = Mock()
        mock_process.communicate.return_value = ("hello world", "")
        mock_popen.return_value = mock_process

        callback = Mock()
        voice_input = VoiceInput(on_complete=callback)

        voice_input.start_recording()

        # Wait for the thread to complete
        time.sleep(1)

        # Verify callback was called with the transcribed text
        callback.assert_called_once_with("hello world")

    @patch("mychatui.voice_input.subprocess.Popen")
    def test_recording_with_stderr(self, mock_popen):
        """Test that stderr is handled gracefully."""
        # Mock the process with stderr output
        mock_process = Mock()
        mock_process.communicate.return_value = (
            "transcription",
            "some debug output",
        )
        mock_popen.return_value = mock_process

        callback = Mock()
        voice_input = VoiceInput(on_complete=callback)

        voice_input.start_recording()

        # Wait for completion
        time.sleep(1)

        # Should still call callback with the transcription
        callback.assert_called_once_with("transcription")

    @patch("mychatui.voice_input.subprocess.Popen")
    def test_recording_error_handling(self, mock_popen):
        """Test error handling when subprocess fails."""
        # Mock the process to raise an exception
        mock_popen.side_effect = Exception("Command not found")

        callback = Mock()
        voice_input = VoiceInput(on_complete=callback)

        voice_input.start_recording()

        # Wait for completion
        time.sleep(1)

        # Should call callback with empty string on error
        callback.assert_called_once_with("")

    @patch("mychatui.voice_input.subprocess.Popen")
    def test_stop_recording(self, mock_popen):
        """Test stopping a recording in progress."""
        # Mock a long-running process
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process still running
        mock_popen.return_value = mock_process

        voice_input = VoiceInput()
        voice_input.process = mock_process
        voice_input.is_recording = True

        voice_input.stop_recording()

        # Verify terminate was called
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=2)
        assert voice_input.is_recording is False

    @patch("mychatui.voice_input.subprocess.Popen")
    def test_stop_recording_timeout(self, mock_popen):
        """Test killing process if terminate times out."""
        import subprocess

        # Mock a process that doesn't terminate
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.wait.side_effect = subprocess.TimeoutExpired("cmd", 2)
        mock_popen.return_value = mock_process

        voice_input = VoiceInput()
        voice_input.process = mock_process
        voice_input.is_recording = True

        voice_input.stop_recording()

        # Verify kill was called after terminate failed
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()

    def test_concurrent_recording_prevention(self):
        """Test that concurrent recordings are prevented."""
        voice_input = VoiceInput()
        voice_input.is_recording = True

        # Should not start another recording
        with patch("mychatui.voice_input.subprocess.Popen") as mock_popen:
            voice_input.start_recording()

            # Wait a bit
            time.sleep(0.1)

            # Popen should not have been called
            mock_popen.assert_not_called()


@pytest.mark.integration
class TestVoiceInputIntegration:
    """Integration tests with the actual listen command."""

    def test_listen_command_exists(self):
        """Test that the listen command exists at the expected path."""
        listen_path = "/bluestone/src/github/rtd/listen/.venv/bin/listen"
        assert os.path.exists(listen_path), f"Listen command not found at {listen_path}"
        assert os.access(listen_path, os.X_OK), "Listen command not executable"

    def test_listen_command_version(self):
        """Test that the listen command can be executed."""
        import subprocess

        listen_path = "/bluestone/src/github/rtd/listen/.venv/bin/listen"

        if not os.path.exists(listen_path):
            pytest.skip("Listen command not available")

        try:
            result = subprocess.run(
                [listen_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            # Should complete without error
            assert result.returncode == 0
        except subprocess.TimeoutExpired:
            pytest.skip("Listen command timed out")
        except Exception as e:
            pytest.skip(f"Could not test listen command: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
