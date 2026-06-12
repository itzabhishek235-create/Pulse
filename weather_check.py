import os
import requests
import sys

def main():
    # 1. Configuration Setup
    # Changing city to Thrissur to match your local area
    CITY = "Thrissur"  
    API_KEY = os.environ.get("OPENWEATHER_API_KEY")
    
    if not API_KEY:
        print("Error: OPENWEATHER_API_KEY secret is not set in GitHub.")
        sys.exit(1)
        
    # 2. Fetch data from OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        print(f"Error fetching data from OpenWeather API: {e}")
        sys.exit(1)
        
    if response.status_code != 200:
        print(f"API Error ({response.status_code}): {data.get('message', 'Unknown error')}")
        sys.exit(1)
        
    # 3. Parse Weather Conditions
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    weather_desc = data["weather"][0]["description"].lower()
    
    print(f"Current weather in {CITY}: {temp}°C, {weather_desc}, Humidity: {humidity}%")
    
    # 4. Check Thresholds for Alert
    # Triggers an alert if it's raining, or if temperature crosses 35°C
    is_raining = "rain" in weather_desc or "drizzle" in weather_desc or "thunderstorm" in weather_desc
    is_too_hot = temp >= 35.0
    
    trigger_alert = "false"
    reason = ""
    
    if is_raining:
        trigger_alert = "true"
        reason = f"Precipitation detected in {CITY}! Current status: {weather_desc.capitalize()} at {temp}°C."
    elif is_too_hot:
        trigger_alert = "true"
        reason = f"High temperature alert for {CITY}! Current temperature is {temp}°C."
        
    # 5. Pass variables forward to the GitHub Actions email step
    # We do this by writing directly to the special GitHub Output environment file
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"trigger={trigger_alert}\n")
            f.write(f"reason={reason}\n")
    else:
        print(f"Local test trigger status: {trigger_alert}. Reason: {reason}")

if __name__ == "__main__":
    main()
