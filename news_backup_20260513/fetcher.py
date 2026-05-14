import json
from typing import List
from pathlib import Path
from datetime import datetime, timezone, timedelta
import feedparser
from email.utils import parsedate_to_datetime
import logging
import time
import requests
from requests.exceptions import Timeout, RequestException, HTTPError
from news.models import NewsItem
from news.utils import load_config, clean_text, is_recent, to_iso_utc


def fetch_single_feed_with_timeout(feed_url: str) -> feedparser.FeedParserDict:
    """
    Scarica un singolo feed RSS con timeout restrittivo (60s) e retry.
    :param feed_url: URL del feed RSS
    :return: Oggetto FeedParserDict (potenzialmente vuoto in caso di timeout/errore)
    """
    max_retries = 3
    retry_delay = 2  # secondi
    timeout_config = (30, 30)  # connect timeout, read timeout: 30s each (total 60s max)

    for attempt in range(max_retries):
        try:
            logging.info(f"Attempt {attempt + 1}/{max_retries} for {feed_url}")
            
            response = requests.get(
                feed_url,
                timeout=timeout_config,
                headers={'User-Agent': 'QuantStudio/1.0 (alberto.sfolcini@outlook.it)'}
            )
            response.raise_for_status()  # Alza HTTPError per 4xx/5xx
            
            feed = feedparser.parse(response.content)
            logging.info(f"Feed {feed_url} scaricato correttamente: {len(feed.entries)} entry")
            return feed
            
        except Timeout:
            if attempt == max_retries - 1:
                logging.warning(f"Timeout después de 60s - Feed: {feed_url}")
                return feedparser.FeedParserDict()
            time.sleep(retry_delay)
        except HTTPError as e:
            logging.error(f"HTTP Error {e.response.status_code} per {feed_url}: {str(e)}")
            return feedparser.FeedParserDict()
        except RequestException as e:
            logging.error(f"Request Error per {feed_url}: {str(e)}")
            return feedparser.FeedParserDict()

def fetch_recent_news(region: str) -> List[NewsItem]:
    from datetime import datetime, timezone
    import requests_cache
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = load_config()
    region = config.get("news_region", region)
    
    # Enable caching per session (TTL configurabile)
    feed_cache_ttl = config.get("feed_cache_ttl", 3600)  # Default: 1 ora
    if feed_cache_ttl > 0:
        requests_cache.install_cache(
            'news_feeds_cache',
            expire_after=feed_cache_ttl,
            backend='sqlite',
            allowable_methods=['GET'],
            cache_control=False  # Force cache TTL
        )
        logging.info(f"Cache HTTP enabled (TTL: {feed_cache_ttl}s)")
    else:
        logging.info("Cache HTTP disabled (feed_cache_ttl <= 0)")
    
    news_items = []
    total_entries = 0
    recent_entries = 0

    logging.info(f"Avvio downloading news per regione: {region}")

    if region not in config.get("news", {}):
        raise ValueError(f"Regione '{region}' non trovata nei feed RSS.")

    today_utc = datetime.now(timezone.utc).date()  # UTC
    yesterday_utc = today_utc - timedelta(days=1)  # UTC yesterday

    for feed_url in config["news"][region]:
        logging.info(f"Downloading feed: {feed_url}")
        try:
            feed = fetch_single_feed_with_timeout(feed_url)

            # Log stato feed
            if feed.get("bozo", False):
                logging.warning(f"Feed malformato: {feed_url}, errore: {feed.bozo_exception}")

            # Stats (now enabled)
            logging.info(f"Trovate {len(feed.entries)} entry nel feed {feed_url}")

            for entry in feed.entries:
                total_entries += 1
                published = entry.get("published") or entry.get("pubDate")

                if not published:
                    logging.debug(f"Entry senza data nel feed {feed_url}: {entry.get('title', 'N/A')}")
                    continue

                try:
                    # Converti la data RFC 2822 in ISO 8601 se necessario
                    if "pubDate" in entry or "published" in entry:
                        published_parsed = parsedate_to_datetime(published)
                        published_iso = published_parsed.isoformat() if published_parsed else None
                    else:
                        published_iso = to_iso_utc(published)

                    if not published_iso:
                        logging.debug(f"Impossibile convertire data per entry in {feed_url}")
                        continue

                except (ValueError, AttributeError) as e:
                    logging.error(f"Errore di parsing data per entry in {feed_url}: {e}")
                    logging.debug(f"Entry problematica: {entry}")
                    continue

                try:
                    # Filtra solo notizie pubblicate OGGI o IERI (UTC)
                    published_date_utc = datetime.fromisoformat(published_iso.replace("Z", "+00:00")).date()
                    if published_date_utc not in {today_utc, yesterday_utc}:
                        continue  # Ignora notizie non di oggi/ieri

                    recent_entries += 1
                    title = entry.get("title", "Senza titolo")
                    summary = clean_text(
                        entry.get("description", "") or
                        entry.get("summary", "") or
                        entry.get("content", "")
                    )
                    link = entry.get("link", "")

                    news_items.append(NewsItem(
                        title=title,
                        summary=summary,
                        source=feed_url,
                        published_at=published_iso,
                        link=link
                    ))
                    logging.info(f"Aggiunta news: {title[:60]}... (data: {published_iso})")

                except (ValueError, AttributeError) as e:
                    logging.error(f"Errore di parsing per entry in {feed_url}: {e}")
                    logging.debug(f"Entry problematica: {entry}")
                    continue
                except Exception as e:
                    logging.error(f"Errore durante il parsing di {feed_url}: {e}")
                    continue

        except Exception as e:
            logging.error(f"Errore durante il parsing di {feed_url}: {e}")
            continue
    
    logging.info(f"Statistiche: {total_entries} totali analizzate, {recent_entries} recenti trovate, {len(news_items)} selezionate")
    
    # Ordina per data (più recenti prima) e limita a 10
    news_items.sort(key=lambda x: x.published_at, reverse=True)
    result_count = len(news_items[:10])
    logging.info(f"Restituite {result_count} news più recenti")
    
    return news_items[:10]
