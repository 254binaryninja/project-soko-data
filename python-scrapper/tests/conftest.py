"""
Shared test configuration and fixtures for NSE scraper tests
"""

import pytest
from unittest.mock import Mock


@pytest.fixture
def sample_nse_html():
    """Sample NSE HTML for testing"""
    return """
    <html>
    <body>
        <table>
            <tbody>
                <tr>
                    <td>ABSA</td>
                    <td>Absa Bank Kenya Plc</td>
                    <td>426,200</td>
                    <td>19.80</td>
                    <td>+0.05</td>
                </tr>
                <tr>
                    <td>BAT</td>
                    <td>British American Tobacco Kenya</td>
                    <td>45,200</td>
                    <td>377.50</td>
                    <td>-1.25</td>
                </tr>
                <tr>
                    <td>NOKCHANGE</td>
                    <td>No Change Stock</td>
                    <td>1,000</td>
                    <td>100.00</td>
                    <td>—</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def mock_redis_instance():
    """Mock Redis instance for testing"""
    mock_redis = Mock()
    mock_redis.ping.return_value = True
    mock_redis.xadd.return_value = b"1234567890-0"
    mock_redis.xtrim.return_value = 5
    return mock_redis


@pytest.fixture
def sample_ticker_data():
    """Sample ticker data for testing"""
    return {
        "ABSA": (19.80, 0.05),
        "BAT": (377.50, -1.25),
        "NOKCHANGE": (100.00, None)
    }
