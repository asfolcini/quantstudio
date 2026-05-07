"""Test for LLM interpretation functionality within EdgeEngine for ticker ISP.MI."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

from edge_engine import EdgeEngine


def load_isp_mi_data():
    """Load historical data for ISP.MI using the existing Yahoo provider."""
    from data.providers.yahoo import YahooProvider
    provider = YahooProvider()
    
    # Download historical data for ISP.MI
    raw_data = provider.download('ISP.MI')
    
    # Prepare the DataFrame with required columns
    df = raw_data.reset_index()
    # Rename columns to match the expected format
    df.columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits']
    df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]
    
    return df


class TestLLMInterpretation:
    """Test suite for LLM interpretation functionality within EdgeEngine."""

    def test_llm_interpretation_with_isp_mi(self):
        """Test _generate_llm_interpretation method for ISP.MI ticker."""
        # Step 1: Load historical data for ISP.MI
        df_isp_mi = load_isp_mi_data()
        
        # Ensure the data is valid (has sufficient rows)
        assert len(df_isp_mi) >= 20, "Insufficient data for ISP.MI"
        
        # Step 2: Initialize EdgeEngine with the data
        engine = EdgeEngine(df_isp_mi)
        
        # Step 3: Mock the LLM API call to avoid external dependency
        # Replace the API call with a predictable response
        mock_llm_response = MagicMock()
        mock_llm_response.status_code = 200
        mock_llm_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'Test LLM interpretation: ISP.MI shows strong market position'
                    }
                }
            ]
        }
        
        # Patch the requests.post call to return the mock response
        with patch('edge_engine.requests.post', return_value=mock_llm_response) as mock_post:
            # Ensure EdgeEngine is configured for LLM usage
            engine.llm_config = {
                'api_url': 'http://fake-api.com',
                'api_key': 'test_key',
                'model': 'auto'
            }
            
            # Step 4: Trigger LLM interpretation
            llm_interpretation = engine._generate_llm_interpretation()
            
            # Assertions
            assert llm_interpretation is not None, "LLM interpretation should not be None"
            assert "Test LLM interpretation" in llm_interpretation, "LLM interpretation should contain expected content"
            
            # Verify the API was called as expected
            mock_post.assert_called_once()

    def test_llm_interpretation_missing_config(self):
        """Test _generate_llm_interpretation when LLM config is missing."""
        # Load historical data for ISP.MI
        df_isp_mi = load_isp_mi_data()
        engine = EdgeEngine(df_isp_mi)
        
        # Ensure LLM config is empty (simulate missing config)
        engine.llm_config = {
            'api_url': '',
            'api_key': ''
        }
        
        # Trigger LLM interpretation (should return None due to missing config)
        llm_interpretation = engine._generate_llm_interpretation()
        
        # Assertions
        assert llm_interpretation is None, "LLM interpretation should be None when config is missing"

    def test_llm_interpretation_api_failure(self):
        """Test _generate_llm_interpretation when the LLM API call fails."""
        # Load historical data for ISP.MI
        df_isp_mi = load_isp_mi_data()
        engine = EdgeEngine(df_isp_mi)
        
        # Mock the LLM API call to simulate a failure
        mock_llm_response = MagicMock()
        mock_llm_response.status_code = 500
        
        with patch('edge_engine.requests.post', return_value=mock_llm_response) as mock_post:
            # Trigger LLM interpretation with API failure
            engine.llm_config = {
                'api_url': 'http://fake-api.com',
                'api_key': 'test_key',
                'model': 'auto'
            }
            
            llm_interpretation = engine._generate_llm_interpretation()
            
            # Assertions
            assert llm_interpretation is None, "LLM interpretation should be None when API call fails"

    def test_llm_interpretation_content_validation(self):
        """Test _generate_llm_interpretation for content validity."""
        # Load historical data for ISP.MI
        df_isp_mi = load_isp_mi_data()
        engine = EdgeEngine(df_isp_mi)
        
        # Mock a realistic LLM response
        mock_llm_response = MagicMock()
        mock_llm_response.status_code = 200
        mock_llm_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': """
                        ISP.MI shows a bullish trend with positive momentum.
                        Market summary: Strong uptrend.
                        Bias: BUY WATCH.
                        Confidence: HIGH.
                        Key levels: S1 at 10.5, R1 at 11.5.
                        Action: Consider long positions.
                        """
                    }
                }
            ]
        }
        
        with patch('edge_engine.requests.post', return_value=mock_llm_response) as mock_post:
            engine.llm_config = {
                'api_url': 'http://fake-api.com',
                'api_key': 'test_key',
                'model': 'auto'
            }
            
            llm_interpretation = engine._generate_llm_interpretation()
            
            # Assertions
            assert llm_interpretation is not None, "LLM interpretation should not be None"
            assert "bullish" in llm_interpretation.lower(), "LLM interpretation should mention trend"
            assert "BUY WATCH" in llm_interpretation, "LLM interpretation should mention bias"
            assert "HIGH" in llm_interpretation, "LLM interpretation should mention confidence"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
