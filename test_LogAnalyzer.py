import unittest
from unittest.mock import patch
from LogAnalyzer import analyze_log_chunk, analyze_logs_in_folder
import os

class TestLogAnalyzer(unittest.TestCase):

    @patch('LogAnalyzer.chain.run')
    def test_analyze_log_chunk(self, mock_run):
        # Mock the return value from OpenAI API
        mock_run.return_value = "Mocked Analysis Result"

        # Simulated log chunk
        log_chunk = "Error: Something went wrong"

        # Run the analyze_log_chunk function
        result = analyze_log_chunk(log_chunk)

        # Assert that the mock API was called and returned the mocked result
        mock_run.assert_called_once()
        self.assertEqual(result, "Mocked Analysis Result")

    @patch('LogAnalyzer.analyze_log_chunk')
    def test_analyze_logs_in_folder(self, mock_analyze_log_chunk):
        # Mock the analyze_log_chunk function to avoid real API call
        mock_analyze_log_chunk.return_value = "Mocked Log Chunk Analysis"

        # Create a temporary directory and log file for testing
        temp_folder = "test_logs"
        os.makedirs(temp_folder, exist_ok=True)

        try:
            # Create a dummy log file
            log_file_path = os.path.join(temp_folder, "test_log.log")
            with open(log_file_path, "w") as log_file:
                log_file.write("Log entry 1\nLog entry 2\nLog entry 3")

            # Run the analyze_logs_in_folder function
            analyze_logs_in_folder(temp_folder)

            # Assert that the analyze_log_chunk function was called
            self.assertTrue(mock_analyze_log_chunk.called)

        finally:
            # Clean up the temporary log file and folder
            if os.path.exists(log_file_path):
                os.remove(log_file_path)
            if os.path.exists(temp_folder):
                os.rmdir(temp_folder)

if __name__ == "__main__":
    unittest.main()
