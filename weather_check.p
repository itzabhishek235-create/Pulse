import os
import requests
import sys

# Configuration
CITY = "Thiruvananthapuram"
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def main():
    if not API_KEY:
        print("Error: Missing OpenWeather API Key.")
        sys.exit(1)

    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        sys.exit(1)

    # Extract conditions
    temp = data["main"]["temp"]
    weather_main = [w["main"].lower() for w in data["weather"]]
    is_raining = "rain" in weather_main or "drizzle" in weather_main

    print(f"Current Condition in {CITY}: Temp={temp}°C, Conditions={weather_main}")

    # Alert condition validation
    should_alert = False
    alert_reason = ""

    if temp > 35:
        should_alert = True
        alert_reason += f"• Extreme Temperature Alert: {temp}°C (Exceeded 35°C Limit)\n"
    if is_raining:
        should_alert = True
        alert_reason += f"• Precipitation Alert: Rain/Drizzle detected.\n"

    # Export to GitHub Environment variables
    if should_alert:
        print("Alert threshold breached! Arming email step...")
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write("trigger=true\n")
            html_reason = alert_reason.replace('\n', '<br>')
            f.write(f"reason=Weather Warning for {CITY}:<br>{html_reason}\n")
    else:
        print("Weather is within safe thresholds. No alert needed.")
        with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
            f.write("trigger=false\n")

if __name__ == "__main__":
    main()
