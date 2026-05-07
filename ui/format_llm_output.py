"""Format LLM output with selective bolding and colors."""

import re


def format_llm_output_rich(text):
    """
    Format LLM output using Rich library with:
    - Text between ** markers: bold and green
    - Numbers: bold and cyan
    - Everything else: unchanged
    """
    try:
        from rich.text import Text
        from rich.console import Console
        
        # Create a Rich Text object
        formatted_text = Text()
        
        # Process the text line by line
        lines = text.split('\n')
        for line in lines:
            if not line.strip():
                formatted_text.append('\n')
                continue
            
            # Split by ** markers
            if '**' in line:
                parts = line.split('**')
                for i, part in enumerate(parts):
                    if i % 2 == 0:  # Outside of **
                        formatted_text.append(part)
                    else:  # Inside ** (bold+underline+green)
                        formatted_text.append(part, style='bold underline green')
                formatted_text.append('\n')
            else:  # No ** markers
                # Find numbers and make them bold cyan
                # This regex matches numbers with optional decimal points
                number_pattern = r'(\d+\.?\d*)'
                segments = re.split(number_pattern, line)
                
                for segment in segments:
                    if re.match(number_pattern, segment):
                        formatted_text.append(segment, style='bold cyan')
                    else:
                        formatted_text.append(segment)
                formatted_text.append('\n')
        
        return formatted_text
        
    except ImportError:
        # Fallback to plain text if Rich is not available
        return text


# Example LLM output
sample_llm_output = """
**Trading Summary (English)**
**Market Summary:**
The market is in a bullish trend with 17.5% momentum. Current price: 128.35.

**Bias:**
BUY WATCH (Score: 75.5)

**Confidence:**
MEDIUM (Level: 3)

**Key Levels:**
- Support: 125.00 (S1), 122.50 (S2)
- Resistance: 130.00 (R1), 132.50 (R2)
- VWAP: 128.15

**Action:**
Consider buying below 127.00 with stop at 124.50 and target at 131.25.
"""


if __name__ == '__main__':
    print("=== LLM Output With Selective Formatting ===")
    print("\n### Original Output ###")
    print(sample_llm_output)
    
    print("\n### Formatted Output (Rich) ###")
    formatted = format_llm_output_rich(sample_llm_output)
    
    # Print the formatted text
    from rich.console import Console
    console = Console()
    console.print(formatted)
    
    print("\n=== Formatting Rules Applied ===")
    print("✅ Text between **: Bold + Underline + Green")
    print("✅ Numbers: Bold + Cyan")
    print("✅ Everything else: Unchanged")
    print("✅ Compatible with all terminals that support ANSI colors")
