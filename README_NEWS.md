# News Module - Monday Morning Version

## What This Version Does

This is the **Monday morning (11:00 AM) version** of the news module that shows:

1. **RAW LLM Payload** in console (complete JSON response from API)
2. **No parsing** of JSON responses
3. **No schema validation** or fallback mechanisms
4. **Simple output format** for debugging purposes

## Usage

```bash
python -m news --region Europe
```

Output will include:
```
=== RAW LLM RESPONSE ===
{
  "id": "abc-123",
  "choices": [{
    "message": {"content": "Analisi delle news per l'Europa: ... "}
  }]
}
=== END RAW LLM RESPONSE ===
```

## Key Characteristics

- ✅ Shows complete raw API response
- ✅ Simple and straightforward error handling
- ✅ No complex prompt engineering
- ✅ Direct console output of raw payload

## Difference from Later Versions

This version **does NOT have**:
- JSON5 parsing for malformed JSON
- Schema validation  
- HTTP caching for RSS feeds
- Timeout handling for slow feeds
- Advanced fallback mechanisms

## Reset Information

This version was restored to match the working state of Monday morning. If you need the enhanced version with parsing and error handling, it can be restored from the backup.