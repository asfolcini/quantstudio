import json
import json5
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import requests
import re
import logging
from jsonschema import validate, ValidationError
from news.models import NewsItem, NewsAnalysis
from news.utils import load_config


# Schema JSON di validazione
NEWS_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "overview": {
            "type": "object",
            "properties": {
                "summary": {"type": "string", "maxLength": 500},
                "key_themes": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["summary", "key_themes"]
        },
        "news": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "impact_score": {"type": ["integer", "null"], "minimum": 1, "maximum": 10},
                    "impact_reason": {"type": "string"}
                },
                "required": ["title", "impact_score", "impact_reason"]
            }
        }
    },
    "required": ["overview", "news"]
}


def call_llm(prompt: str) -> str:
    config = load_config()
    llm_config = config.get("llm", {})
    url = llm_config.get("api_url")
    api_key = llm_config.get("api_key")
    
    if not url or not api_key:
        raise ValueError("LLM API URL o API key non configurati.")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Payload conforme all'esempio curl funzionante
    payload = {
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        response_data = response.json()
        content = response_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return content.strip() if content else ""
    except requests.exceptions.RequestException as e:
        logging.error(f"LLM HTTP Error: {response.status_code} - {e}")
        return ""
    except Exception as e:
        logging.error(f"LLM Generic Error: {e}")
        return ""
    except Exception as e:
        print(f"LLM Error: {e}")
        return ""


def build_prompt(region: str, news_items: List[NewsItem]) -> str:
    from datetime import datetime, timezone
    language = load_config().get("report_language", "italian")

    news_list = "\n".join([
        f"- {item.title}: {item.summary}"
        for item in news_items
    ])

    # Data odierna (per prompt, per coerenza con fetch_recent_news)
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    time_range = {
        "from": f"{today_utc}T00:00:00Z",
        "to": f"{today_utc}T23:59:59Z"
    }

    prompt = f"""
    Sei un esperto finanziario. Analizza le seguenti notizie per la regione {region}, pubblicate tra {time_range['from']} e {time_range['to']}.
    Scrivi in {language}.

    Istruzioni STRETTE:
    1. Riassumi sintetico (max 100 parole) gli eventi con maggiore impatto sui mercati, identificando i settori più rilevanti.
    2. Assegna un impact_score (da 1 a 10) alle singole notizie in base al loro potenziale effetto sul mercato.
    3. Indica i ticker o ETF più rilevanti (se presenti nelle news).
    4. PROIBITO: Nessun testo fuori dal JSON. Nessun markdown, commenti, o note. Usa ESCLUSIVAMENTE virgolette doppie e assicurati che il JSON sia ben formattato.

    Formato corretto:
    ###JSON_START###
    {{
      "overview": {{
        "summary": "stringa in {language}",
        "key_themes": ["settore1", "settore2"]
      }},
      "news": [
        {{
          "title": "titolo esatto da {news_list}",
          "impact_score": 1-10,
          "impact_reason": "motivazione in {language}"
        }}
      ]
    }}
    ###JSON_END###

    Esempi di errori da evitare:
    - Commenti nel JSON: // commento ❌
    - Markdown delimiters: ```json ... ``` ❌
    - Virgolette non escaped: \" testo \" ❌

    Notizie:
{news_list}
    """
    return prompt


def parse_llm_response(response_text: str, news_items: List[NewsItem]) -> Dict[str, Any]:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Log dell'output grezzo per debug AVANZATO
    logging.info(f"Output LLM grezzo (primi 2000 chars): {response_text[:2000]}")
    
    # FALLBACK PREPARATION: Preparing titles list for fallback
    fallback_news = []
    if news_items:
        fallback_news = [{"title": item.title} for item in news_items]
    
    try:
        # Step 1: Try to extract JSON between delimiters (preferred method)
        json_match = re.search(r'###JSON_START###([\s\S]*?)###JSON_END###', response_text)
        if not json_match:
            # Fallback 1: Attempt to extract any JSON block
            json_match = re.search(r'\{["\n\s\S]*\}', response_text)
            if not json_match:
                raise ValueError("No JSON block found in response")
        
        json_str = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group()
        json_str = json_str.strip()
        
        # Step 2: Parse with json5 for tolerance (handles trailing commas, single quotes)
        data = json5.loads(json_str)
        
        # Step 3: Validate schema
        validate(instance=data, schema=NEWS_ANALYSIS_SCHEMA)
        
        return data
        
    except ValueError as e:
        if "No JSON block found" in str(e):
            logging.error(f"No JSON block found in LLM response")
        else:
            logging.error(f"Unexpected ValueError: {e}")
    except Exception as e:
        logging.error(f"Parsing error (likely json5 or validation): {e}")
        logging.error(f"Raw JSON string attempt: {json_str[:200] if 'json_str' in locals() else 'No JSON extracted'}")
    
    # Enhanced Fallback: Full debug capture
    fallback = {
        "overview": {
            "summary": "Fallback: JSON malformato. Check _debug per analisi tecnica.",
            "key_themes": []
        },
        "news": fallback_news,
        "_debug": {
            "snapshot_raw_output": response_text,
            "fallback_reason": "LLM JSON parsing/validation failure",
            "fallback_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "fetailed_errors": {
                "missing_keys": [],
                "extra_keys": []
            }
        }
    }
    logging.warning("Fallback mode activated. Full LLM output logged for debugging.")
    return fallback


def generate_analysis(region: str, news_items: List[NewsItem]) -> Dict[str, Any]:
    prompt = build_prompt(region, news_items)
    llm_response = call_llm(prompt)
    analysis = parse_llm_response(llm_response, news_items)
    
    # Unisci i dati
    for item in analysis.get("news", []):
        for news in news_items:
            if item.get("title") == news.title:
                item.update({
                    "summary": news.summary,
                    "source": news.source,
                    "published_at": news.published_at,
                    "link": news.link
                })
                break
    
    return analysis




def save_analysis(region: str, analysis: Dict[str, Any]) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    cache_dir = Path(__file__).parent.parent / "cache"
    cache_dir.mkdir(exist_ok=True)  # Crea la cartella cache se non esiste
    output_path = cache_dir / f"analysis_{region}_{timestamp}.json"

    metadata = {
        "region": region,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "time_range": {
            "from": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(timespec="seconds").replace("+00:00", "Z"),
            "to": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        },
        "total_news": len(analysis.get("news", [])),
        "feeds_used": load_config()["news"][region],
        "report_language": load_config().get("report_language", "italian")
    }

    final_analysis = {
        "metadata": metadata,
        "news": analysis.get("news", []),
        "overview": analysis.get("overview", {"summary": "Nessuna panoramica.", "key_themes": []})
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_analysis, f, indent=2, ensure_ascii=False)

    return output_path
