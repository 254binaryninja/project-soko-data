"""Tests for fetcher module"""

import pytest
from unittest.mock import patch, Mock
import requests
from fetcher import fetch_html


class TestFetchHTML:
    """Test cases for HTML fetcher"""

    @patch('fetcher.requests.Session')
    def test_successful_fetch(self, mock_session):
        """Test successful HTML fetch"""
        # Setup mock
        mock_response = Mock()
        mock_response.text = "<html>Test content</html>"
        mock_session.return_value.get.return_value = mock_response
        
        result = fetch_html("https://example.com")
        
        assert result == "<html>Test content</html>"
        mock_session.return_value.get.assert_called_once_with(
            "https://example.com", timeout=10.0
        )

    @patch('fetcher.requests.Session')
    def test_http_error_with_retries(self, mock_session):
        """Test HTTP error handling with retries"""
        # Setup mock to raise HTTP error
        mock_session.return_value.get.side_effect = requests.exceptions.HTTPError("404 Not Found")
        
        with patch('fetcher.time.sleep'):  # Mock sleep to speed up test
            result = fetch_html("https://example.com", retries=2)
        
        assert result is None
        assert mock_session.return_value.get.call_count == 2

    @patch('fetcher.requests.Session')
    def test_connection_error_with_retries(self, mock_session):
        """Test connection error handling with retries"""
        # Setup mock to raise connection error
        mock_session.return_value.get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with patch('fetcher.time.sleep'):  # Mock sleep to speed up test
            result = fetch_html("https://example.com", retries=3)
        
        assert result is None
        assert mock_session.return_value.get.call_count == 3

    @patch('fetcher.requests.Session')
    def test_timeout_error(self, mock_session):
        """Test timeout error handling"""
        # Setup mock to raise timeout error
        mock_session.return_value.get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with patch('fetcher.time.sleep'):
            result = fetch_html("https://example.com", timeout=5.0, retries=1)
        
        assert result is None

    @patch('fetcher.requests.Session')
    def test_success_after_retry(self, mock_session):
        """Test successful fetch after initial failure"""
        # Setup mock to fail first, then succeed
        mock_response = Mock()
        mock_response.text = "<html>Success after retry</html>"
        
        mock_session.return_value.get.side_effect = [
            requests.exceptions.ConnectionError("First attempt failed"),
            mock_response
        ]
        
        with patch('fetcher.time.sleep'):
            result = fetch_html("https://example.com", retries=2)
        
        assert result == "<html>Success after retry</html>"
        assert mock_session.return_value.get.call_count == 2

    @patch('fetcher.requests.Session')
    def test_custom_timeout(self, mock_session):
        """Test custom timeout parameter"""
        mock_response = Mock()
        mock_response.text = "<html>Custom timeout test</html>"
        mock_session.return_value.get.return_value = mock_response
        
        result = fetch_html("https://example.com", timeout=30.0)
        
        assert result == "<html>Custom timeout test</html>"
        mock_session.return_value.get.assert_called_once_with(
            "https://example.com", timeout=30.0
        )

    @patch('fetcher.requests.Session')
    def test_headers_are_set(self, mock_session):
        """Test that proper headers are set"""
        mock_response = Mock()
        mock_response.text = "<html>Headers test</html>"
        mock_session.return_value.get.return_value = mock_response
        
        result = fetch_html("https://example.com")
        
        # Verify session headers were updated
        mock_session.return_value.headers.update.assert_called_once()
        
        # Check that User-Agent header was included
        headers_call_args = mock_session.return_value.headers.update.call_args[0][0]
        assert "User-Agent" in headers_call_args
        assert "NSE-Scraper" in headers_call_args["User-Agent"]

    @patch('fetcher.logger')
    @patch('fetcher.requests.Session')
    def test_logging_on_failure(self, mock_session, mock_logger):
        """Test that failures are properly logged"""
        mock_session.return_value.get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with patch('fetcher.time.sleep'):
            result = fetch_html("https://example.com", retries=1)
        
        assert result is None
        mock_logger.warning.assert_called()
        mock_logger.error.assert_called()
