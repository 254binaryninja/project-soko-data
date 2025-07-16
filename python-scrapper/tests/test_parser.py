"""Tests for parser module"""

import pytest
from unittest.mock import patch
from parser import parse_nse


class TestParseNSE:
    """Test cases for NSE parser"""

    def test_parse_empty_html(self):
        """Test parsing empty HTML"""
        result = parse_nse("")
        assert result == {}

    def test_parse_no_table(self):
        """Test parsing HTML with no table"""
        html = "<html><body><p>No table here</p></body></html>"
        result = parse_nse(html)
        assert result == {}

    def test_parse_valid_nse_table(self):
        """Test parsing valid NSE table structure"""
        html = """
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
                </tbody>
            </table>
        </body>
        </html>
        """
        result = parse_nse(html)
        
        assert len(result) == 2
        assert "ABSA" in result
        assert "BAT" in result
        
        # Check price and change for ABSA
        price, change = result["ABSA"]
        assert price == 19.80
        assert change == 0.05
        
        # Check price and change for BAT
        price, change = result["BAT"]
        assert price == 377.50
        assert change == -1.25

    def test_parse_table_with_missing_change(self):
        """Test parsing table where some rows have no change data"""
        html = """
        <html>
        <body>
            <table>
                <tbody>
                    <tr>
                        <td>ABSA</td>
                        <td>Absa Bank Kenya Plc</td>
                        <td>426,200</td>
                        <td>19.80</td>
                        <td>—</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        result = parse_nse(html)
        
        assert len(result) == 1
        price, change = result["ABSA"]
        assert price == 19.80
        assert change is None

    def test_parse_table_with_insufficient_cells(self):
        """Test parsing table with rows that have insufficient cells"""
        html = """
        <html>
        <body>
            <table>
                <tbody>
                    <tr>
                        <td>ABSA</td>
                        <td>Absa Bank Kenya Plc</td>
                    </tr>
                    <tr>
                        <td>BAT</td>
                        <td>British American Tobacco Kenya</td>
                        <td>45,200</td>
                        <td>377.50</td>
                        <td>-1.25</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        result = parse_nse(html)
        
        # Only BAT should be parsed (ABSA has insufficient cells)
        assert len(result) == 1
        assert "BAT" in result
        assert "ABSA" not in result

    def test_parse_invalid_price_format(self):
        """Test parsing with invalid price format"""
        html = """
        <html>
        <body>
            <table>
                <tbody>
                    <tr>
                        <td>ABSA</td>
                        <td>Absa Bank Kenya Plc</td>
                        <td>426,200</td>
                        <td>invalid_price</td>
                        <td>+0.05</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        result = parse_nse(html)
        
        # Should skip invalid price row
        assert len(result) == 0

    def test_parse_price_with_commas(self):
        """Test parsing prices with comma formatting"""
        html = """
        <html>
        <body>
            <table>
                <tbody>
                    <tr>
                        <td>EXPENSIVE</td>
                        <td>Expensive Stock</td>
                        <td>1,000</td>
                        <td>1,234.56</td>
                        <td>+10.50</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        result = parse_nse(html)
        
        assert len(result) == 1
        price, change = result["EXPENSIVE"]
        assert price == 1234.56
        assert change == 10.50

    @patch('parser.logger')
    def test_logging_behavior(self, mock_logger):
        """Test that appropriate logging occurs"""
        html = """
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
                </tbody>
            </table>
        </body>
        </html>
        """
        result = parse_nse(html)
        
        # Verify info logging was called
        mock_logger.info.assert_called_once()
        assert "Parsed 1 tickers from NSE table" in str(mock_logger.info.call_args)
