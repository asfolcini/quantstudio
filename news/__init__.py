"""
Minimal news module - Monday morning version (11:00 AM)
Shows RAW LLM payload, no parsing, no enhancements
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import requests
import feedparser
from email.utils import parsedate_to_datetime
import logging
import typing


def call_llm(prompt: str) -> str:
    """
    Raw LLM API call - shows complete JSON response
    No modifications, pure API output
    """
    config = {"llm": {"api_url": "https://api.openai.com/v1/chat/completions", "api_key": "sk-your-key"}}
    llm_config = config.get("llm", {})
    url = llm_config.get("api_url")
    api_key = llm_config.get("api_key")
    
    if not url or not api_key:
        raise ValueError("Please configure your LLM API credentials in config.json")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    response_data = response.json()
    
    # Show complete raw payload
    print("=== RAW LLM RESPONSE ===")
    print(json.dumps(response_data, indent=2))
    print("=== END RAW LLM RESPONSE ===")
    
    content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return content.strip()


def parse_llm_response(response_text: str, news_items: List[Dict]) -> Dict[str, Any]:
    """
    Super simple parser - just return raw text in a dict
    No schema, no validation - Monday morning style
    """
    return {
        "raw_llm_output": response_text,
        "news": news_items
    }


def generate_analysis(region: str) -> Dict[str, Any]:
    """Minimal wrapper"""
    prompt = f"Analyze {region} news"  # No complex prompt building
    llm_response = call_llm(prompt)
    analysis = parse_llm_response(llm_response, [])
    return analysis


if __name__ == "__main__":
    print("News module - Monday morning version")
    print("Type: python -m news --region Europe to test")