import os
import smtplib
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

def fetch_rss_headlines(url, source_name, limit=5):
    """Fetches and parses the top stories from an XML RSS feed."""
    headlines = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Skipping {source_name}: HTTP {response.status_code}")
            return headlines
            
        root = ET.fromstring(response.content)
        # Find all <item> tags in the RSS feed XML
        items = root.findall(".//item")
        
        for item in items[:limit]:
            title = item.find("title").text if item.find("title") is not None else "No Title"
            link = item.find("link").text if item.find("link") is not None else "#"
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else "N/A"
            
            # Clean up messy publication strings if necessary
            if pub_date != "N/A":
                pub_date = pub_date.replace(" +0530", "").replace(" GMT", "")
            
            headlines.append({
                "title": title.strip(),
                "link": link.strip(),
                "time": pub_date.strip()
            })
    except Exception as e:
        print(f"Error fetching from {source_name}: {e}")
        
    return headlines

def generate_html_body(all_news):
    """Compiles the scraped data arrays into a styled HTML format template."""
    today_str = datetime.now().strftime("%d %B %Y")
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 25px; border-radius: 8px; border: 1px solid #e0e0e0;">
            <h2 style="color: #004085; border-bottom: 2px solid #004085; padding-bottom: 10px; margin-top: 0;">
                📰 Morning News Briefing — {today_str}
            </h2>
            <p style="font-size: 14px; color: #666;">Here are the top headlines gathered for you this morning:</p>
    """
    
    for source, articles in all_news.items():
        if not articles:
            continue
        html += f"""
            <h3 style="color: #111; margin-top: 25px; margin-bottom: 10px; background-color: #f1f3f5; padding: 6px 10px; border-left: 4px solid #007bff;">
                {source}
            </h3>
            <ul style="padding-left: 20px; margin: 0;">
        """
        for art in articles:
            html += f"""
                <li style="margin-bottom: 12px; line-height: 1.4;">
                    <a href="{art['link']}" style="color: #0056b3; font-weight: bold; text-decoration: none;">{art['title']}</a>
                    <br><span style="font-size: 11px; color: #888;">Published: {art['time']}</span>
                </li>
            """
        html += "</ul>"
        
    html += """
            <hr style="border: 0; border-top: 1px solid #e0e0e0; margin-top: 30px;">
            <p style="font-size: 11px; color: #aaa; text-align: center; margin-bottom: 0;">
                Automated Content Delivery Pipeline • Built with Python & GitHub Actions
            </p>
        </div>
    </body>
    </html>
    """
    return html

def send_email(html_content):
    """Establishes an encrypted SMTP link and sends out the HTML packet."""
    sender_email = os.environ.get("EMAIL_USERNAME")
    password = os.environ.get("EMAIL_PASSWORD")
    
    if not sender_email or not password:
        print("Error: SMTP Email Credentials missing from environment.")
        sys.exit(1)
        
    # Constructing standard MIME email heads manually
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"📬 Your Morning News Briefing - {datetime.now().strftime('%d %b')}"
    msg["From"] = f"Daily News Bot <{sender_email}>"
    msg["To"] = sender_email
    
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, sender_email, msg.as_string())
        print("Email dispatched successfully!")
    except Exception as e:
        print(f"Failed to transmit email payload: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Aggregating RSS streams
    feeds = {
        "The Hindu — National": "https://www.thehindu.com/news/national/feeder/default.rss",
        "NDTV — Top Stories": "https://feeds.feedburner.com/ndtvnews-top-stories",
        "India Today — Latest News": "https://www.indiatoday.in/rss/home"
    }
    
    compiled_news = {}
    for source, url in feeds.items():
        print(f"Scraping headlines from {source}...")
        compiled_news[source] = fetch_rss_headlines(url, source, limit=4)
        
    # Check if we have any headlines at all before sending
    if any(compiled_news.values()):
        email_body = generate_html_body(compiled_news)
        send_email(email_body)
    else:
        print("No headlines fetched. Aborting email send.")
        
