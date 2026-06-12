import requests
from datetime import date

# 4.2 Function 1 — get_weather
def get_weather(city="Thiruvananthapuram"):
    """Fetch today's weather as a one-line text summary."""
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()  # remove trailing newline
    except Exception as e:
        return f"Weather unavailable ({e})"

# 4.3 Function 2 — get_quote
def get_quote():
    """Fetch a random motivational quote from ZenQuotes."""
    url = "https://zenquotes.io/api/random"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()  # JSON -> Python list
        quote = data[0]["q"]
        author = data[0]["a"]
        return f'"{quote}" - {author}'
    except Exception as e:
        return f"Quote unavailable ({e})"

# 4.4 Function 3 — build_summary
def build_summary():
    """Assemble the full daily summary from all data sources."""
    today = date.today().strftime("%A, %d %B %Y")
    weather = get_weather()
    quote = get_quote()
    
    summary = f"""==============================
PULSE - Daily Summary
{today}
==============================

WEATHER
{weather}

TODAY'S QUOTE
{quote}

==============================
"""
    return summary

# 4.5 Function 4 — run (the boss)
def run():
    """Main entry point. Called by GitHub Actions."""
    summary = build_summary()
    print(summary)  # shows in the Actions log
    
    # Save to a file (uploaded as a downloadable artifact)
    with open("daily_summary.txt", "w", encoding="utf-8") as f:
        f.write(summary)
        
    print("Pulse ran successfully.")

if __name__ == "__main__":
    run()


