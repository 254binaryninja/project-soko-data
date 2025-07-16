"""Tests for main module"""

import pytest
from unittest.mock import patch, Mock
from main import job, main


class TestJob:
    """Test cases for the main job function"""

    @patch('main.RedisStreamer')
    @patch('main.parse_nse')
    @patch('main.fetch_html')
    def test_successful_job_execution(self, mock_fetch, mock_parse, mock_streamer_class):
        """Test successful job execution"""
        # Setup mocks
        mock_fetch.return_value = "<html>test</html>"
        mock_parse.return_value = {"ABSA": (19.80, 0.05)}
        mock_streamer = Mock()
        mock_streamer_class.return_value = mock_streamer

        # Execute job
        job()

        # Verify calls
        mock_fetch.assert_called_once()
        mock_parse.assert_called_once_with("<html>test</html>")
        mock_streamer.publish_changes.assert_called_once_with({"ABSA": (19.80, 0.05)})

    @patch('main.RedisStreamer')
    @patch('main.parse_nse')
    @patch('main.fetch_html')
    def test_job_with_fetch_failure(self, mock_fetch, mock_parse, mock_streamer_class):
        """Test job when fetch fails"""
        # Setup mocks
        mock_fetch.return_value = None

        # Execute job
        job()

        # Verify parse and streamer were not called
        mock_parse.assert_not_called()
        mock_streamer_class.assert_not_called()

    @patch('main.RedisStreamer')
    @patch('main.parse_nse')
    @patch('main.fetch_html')
    def test_job_with_parse_failure(self, mock_fetch, mock_parse, mock_streamer_class):
        """Test job when parse returns no data"""
        # Setup mocks
        mock_fetch.return_value = "<html>test</html>"
        mock_parse.return_value = {}

        # Execute job
        job()

        # Verify streamer was not called
        mock_streamer_class.assert_not_called()

    @patch('main.RedisStreamer')
    @patch('main.parse_nse')
    @patch('main.fetch_html')
    def test_job_with_exception(self, mock_fetch, mock_parse, mock_streamer_class):
        """Test job handles exceptions gracefully"""
        # Setup mocks to raise exception
        mock_fetch.side_effect = Exception("Network error")

        # Execute job (should not raise exception)
        job()

        # Verify other functions weren't called
        mock_parse.assert_not_called()
        mock_streamer_class.assert_not_called()


class TestMain:
    """Test cases for the main function"""

    @patch('main.scheduler.schedule_job')
    @patch('main.setup_logging')
    def test_main_function(self, mock_setup_logging, mock_schedule_job):
        """Test main function execution"""
        # Setup mock to avoid infinite loop
        mock_schedule_job.side_effect = KeyboardInterrupt()

        # Execute main - should handle KeyboardInterrupt gracefully
        main()

        # Verify setup was called
        mock_setup_logging.assert_called_once()
        mock_schedule_job.assert_called_once()

    @patch('main.scheduler.schedule_job')
    @patch('main.setup_logging')
    def test_main_with_exception(self, mock_setup_logging, mock_schedule_job):
        """Test main function handles exceptions"""
        # Setup mock to raise exception
        mock_schedule_job.side_effect = Exception("Scheduler error")

        # Execute main
        with pytest.raises(Exception):
            main()

        mock_setup_logging.assert_called_once()
