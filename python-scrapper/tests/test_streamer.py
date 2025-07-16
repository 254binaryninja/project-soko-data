"""Tests for streamer module"""

import pytest
from typing import Dict, Tuple, Optional
from unittest.mock import patch, Mock, MagicMock
from redis.exceptions import ConnectionError as RedisConnectionError
from streamer import RedisStreamer


class TestRedisStreamer:
    """Test cases for Redis streamer"""

    @patch('streamer.redis.Redis.from_url')
    def test_successful_initialization(self, mock_redis):
        """Test successful Redis streamer initialization"""
        # Setup mock Redis instance
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        streamer = RedisStreamer()
        
        assert streamer.r == mock_redis_instance
        assert streamer.last_prices == {}
        mock_redis_instance.ping.assert_called_once()


    @patch('streamer.redis.Redis.from_url')
    @patch('streamer.config')
    def test_publish_new_ticker(self, mock_config, mock_redis):
        """Test publishing data for new ticker"""
        # Setup config
        mock_config.TIMESTAMP_MS = False
        mock_config.STREAM_NAME = "test:stream"
        mock_config.STREAM_MAXLEN = 1000
        
        # Setup mock Redis
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        streamer = RedisStreamer()
        
        # Test data
        data: Dict[str, Tuple[float, Optional[float]]] = {"ABSA": (19.80, 0.05)}
        
        with patch('streamer.time.time', return_value=1642694400):
            streamer.publish_changes(data)
        
        # Verify xadd was called
        mock_redis_instance.xadd.assert_called_once()
        
        # Check the fields that were passed
        call_args = mock_redis_instance.xadd.call_args
        fields = call_args[1]['fields']
        
        assert fields['ticker'] == 'ABSA'
        assert fields['price'] == '19.8'
        assert fields['price_change'] == '0.05'
        assert fields['price_change_direction'] == 'up'

    @patch('streamer.redis.Redis.from_url')
    @patch('streamer.config')
    def test_publish_no_change(self, mock_config, mock_redis):
        """Test that no data is published when price hasn't changed"""
        # Setup config
        mock_config.TIMESTAMP_MS = False
        mock_config.STREAM_NAME = "test:stream"
        mock_config.STREAM_MAXLEN = 1000
        
        # Setup mock Redis
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        streamer = RedisStreamer()
        
        # Set existing price
        streamer.last_prices["ABSA"] = 19.80
        
        # Test data with same price
        data = {"ABSA": (19.80, 0.00)}
        
        streamer.publish_changes(data) # type: ignore
        
        # Verify xadd was NOT called
        mock_redis_instance.xadd.assert_not_called()

    @patch('streamer.redis.Redis.from_url')
    @patch('streamer.config')
    def test_publish_price_change(self, mock_config, mock_redis):
        """Test publishing when price has changed"""
        # Setup config
        mock_config.TIMESTAMP_MS = False
        mock_config.STREAM_NAME = "test:stream"
        mock_config.STREAM_MAXLEN = 1000
        
        # Setup mock Redis
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        streamer = RedisStreamer()
        
        # Set existing price
        streamer.last_prices["ABSA"] = 19.80
        
        # Test data with different price
        data = {"ABSA": (20.00, 0.20)}
        
        with patch('streamer.time.time', return_value=1642694400):
            streamer.publish_changes(data) # type: ignore
        
        # Verify xadd was called
        mock_redis_instance.xadd.assert_called_once()
        
        # Check calculated change fields
        call_args = mock_redis_instance.xadd.call_args
        fields = call_args[1]['fields']
        
        assert float(fields['calculated_change']) == pytest.approx(0.2, abs=1e-10)
        assert 'calculated_pct_change' in fields

    @patch('streamer.redis.Redis.from_url')
    @patch('streamer.config')
    def test_publish_negative_change(self, mock_config, mock_redis):
        """Test publishing with negative price change"""
        # Setup config
        mock_config.TIMESTAMP_MS = False
        mock_config.STREAM_NAME = "test:stream"
        mock_config.STREAM_MAXLEN = 1000
        
        # Setup mock Redis
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        streamer = RedisStreamer()
        
        # Test data with negative change
        data = {"ABSA": (19.75, -0.05)}
        
        with patch('streamer.time.time', return_value=1642694400):
            streamer.publish_changes(data) # type: ignore
        
        # Check price change direction
        call_args = mock_redis_instance.xadd.call_args
        fields = call_args[1]['fields']
        
        assert fields['price_change_direction'] == 'down'
        assert fields['price_change'] == '-0.05'

    @patch('streamer.redis.Redis.from_url')
    @patch('streamer.config')
    def test_publish_no_change_data(self, mock_config, mock_redis):
        """Test publishing when change data is None"""
        # Setup config
        mock_config.TIMESTAMP_MS = False
        mock_config.STREAM_NAME = "test:stream"
        mock_config.STREAM_MAXLEN = 1000
        
        # Setup mock Redis
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis.return_value = mock_redis_instance
        
        streamer = RedisStreamer()
        
        # Test data with None change
        data = {"ABSA": (19.80, None)}
        
        with patch('streamer.time.time', return_value=1642694400):
            streamer.publish_changes(data) # type: ignore
        
        # Check that price_change fields are not included
        call_args = mock_redis_instance.xadd.call_args
        fields = call_args[1]['fields']
        
        assert 'price_change' not in fields
        assert 'price_change_direction' not in fields
        assert fields['ticker'] == 'ABSA'
        assert fields['price'] == '19.8'

    @patch('streamer.redis.Redis.from_url')
    @patch('streamer.config')
    def test_trim_by_age(self, mock_config, mock_redis):
        """Test stream trimming by age"""
        # Setup config
        mock_config.TIMESTAMP_MS = True
        mock_config.STREAM_NAME = "test:stream"
        
        # Setup mock Redis
        mock_redis_instance = Mock()
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.xtrim.return_value = 5  # 5 entries removed
        mock_redis.return_value = mock_redis_instance
        
        streamer = RedisStreamer()
        
        with patch('streamer.time.time', return_value=1642694400):
            streamer._trim_by_age(min_age_sec=3600)
        
        # Verify xtrim was called with correct parameters
        mock_redis_instance.xtrim.assert_called_once()
        call_args = mock_redis_instance.xtrim.call_args
        
        assert call_args[0][0] == "test:stream"  # stream name
        assert 'minid' in call_args[1]
