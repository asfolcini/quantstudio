if __name__ == "__main__":
    import argparse
    from news.fetcher import fetch_recent_news
    from news.analyzer import generate_analysis, save_analysis
    
    # Crea parser per i flag
    parser = argparse.ArgumentParser(description='QuantStudio News Analyzer')
    parser.add_argument('--region', default='Europe', help='Regione di interesse (default: Europe)')
    args = parser.parse_args()
    
    # Scarica news e genera analisi
    news_items = fetch_recent_news(args.region)
    
    if not news_items:
        print("Nessuna notizia recente trovata.")
        exit(0)
    
    analysis = generate_analysis(args.region, news_items)
    output_path = save_analysis(args.region, analysis)
    print(f"Analisi salvata in: {output_path}")
