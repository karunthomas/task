'''
Author: Karun Thomas
Date: 20-06-2023
'''
import logging

logging.basicConfig(filename='crawler.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import sqlite3
    import requests
    from urllib.parse import urlparse, urljoin
except ImportError as e:
    logging.error(f"Error while Importing: {str(e)}")

def getdomain(url):
    # Domain name exraction
    parsed_url = urlparse(url)
    return parsed_url.netloc

def database():
    # Database creation
    try:
        conn = sqlite3.connect('crawler.db')
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='web_links'")
        table_exists = c.fetchone()
        if not table_exists:
            c.execute('''
                CREATE TABLE IF NOT EXISTS web_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    domain TEXT
                )
            ''')
            conn.commit()
            conn.close()
            logging.info("web_links table created.")
        else:
            logging.info("Table already exists.")
            print("Table already exists.")
    except Exception as e:
        logging.error(f"Error creating database: {str(e)}")

def exists(url):
    # Check link already in db
    try:
        conn = sqlite3.connect('crawler.db')
        c = conn.cursor()
        c.execute("SELECT * FROM web_links WHERE url=?", (url,))
        result = c.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logging.error(f"Error while checking link in db: {str(e)}")

def crawl(url):
    domain = getdomain(url)
    if not exists(url):
        print(f"Crawling: {url}")
        try:
            conn = sqlite3.connect('crawler.db')
            c = conn.cursor()
            c.execute("INSERT INTO web_links (url, domain) VALUES (?, ?)", (url, domain))
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"Error insert links '{url}' in the database: {str(e)}")
        try:
            response = requests.get(url)
            if response.status_code == 200:
                for link in extract(response.text):
                    absolute_link = urljoin(url, link)
                    link_domain = getdomain(absolute_link)
                    if domain == link_domain:
                        crawl(absolute_link)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error crawling {url}: {str(e)}")
            print(f"Error crawling {url}: {str(e)}")

def extract(content):
    # Extract links from website
    import re
    try:
        link_pattern = re.compile(r'<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
        links = link_pattern.findall(content)
        return links
    except Exception as e:
            logging.error(f"Error while extact links from HTML : {str(e)}")
        

def display():
    # Print all from database
    try:
        conn = sqlite3.connect('crawler.db')
        c = conn.cursor()
        c.execute("SELECT * FROM web_links")
        rows = c.fetchall()
        for row in rows:
            print(row[0],row[2],row[1])
        conn.close()
    except Exception as e:
            logging.error(f"Error while printing links: {str(e)}")
        
def main():
    database()
    url = "https://bugatti-smartwatches.com/"
    crawl(url)
    #display()

if __name__ == '__main__':
    main()
