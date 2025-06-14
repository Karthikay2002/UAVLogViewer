# logdoc_scraper.py
import requests
from bs4 import BeautifulSoup
import json

URL = "https://ardupilot.org/plane/docs/logmessages.html"
OUTPUT_JSON = "log_docs.json"

def scrape_log_messages():
    try:
        response = requests.get(URL)
        response.raise_for_status()  # Check for HTTP request errors
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    tables = soup.find_all("table")
    all_logs = []

    for table in tables:
        headers = [th.text.strip().lower() for th in table.find_all("th")]
        for row in table.find_all("tr")[1:]:
            cols = row.find_all(["td", "th"])
            values = [td.text.strip() for td in cols]
            if len(values) < 2:
                continue

            log = {}
            for i, val in enumerate(values):
                key = headers[i] if i < len(headers) else f"col_{i}"
                log[key] = val

            all_logs.append(log)

    with open(OUTPUT_JSON, "w") as f:
        json.dump(all_logs, f, indent=2)

    print(f"[✔] Extracted {len(all_logs)} log entries into {OUTPUT_JSON}")

if __name__ == "__main__":
    scrape_log_messages()
