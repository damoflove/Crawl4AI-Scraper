import asyncio
import pandas as pd
import streamlit as st
from crawl4ai import AsyncWebCrawler
from crawl4ai.extractors import RegexExtractor, XPathExtractor, CSSExtractor

async def scrape_zillow(url):
    async with AsyncWebCrawler() as crawler:
        config = {
            "bypass_cloudflare": True,
            "use_proxies": True,
            "proxy_type": "datacenter",
            "random_user_agent": True,
            "headless": True,
            "scroll_to_bottom": True,
            "wait_for_selector": "[data-testid='property-card']",
            "wait_time": 5
        }
        result = await crawler.arun(url=url, strategy="dynamic", **config)
        
        extractor = RegexExtractor()
        patterns = {
            "price": CSSExtractor("[data-testid='price']"),
            "address": CSSExtractor("[data-testid='address']"),
            "beds": XPathExtractor("//*[contains(text(), 'bd')]/preceding-sibling::span"),
            "baths": XPathExtractor("//*[contains(text(), 'ba')]/preceding-sibling::span"),
            "sqft": XPathExtractor("//*[contains(text(), 'sqft')]/preceding-sibling::span"),
            "link": CSSExtractor("a@href")
        }
        extracted = extractor.extract(result.html, patterns=patterns)
        return extracted['matches']

# Streamlit Interface
st.title("Zillow Scraper with Crawl4ai")
url = st.text_input("Enter Zillow URL:", value="https://www.zillow.com/seattle-wa-98105/rentals/")

if st.button("Start Scraping"):
    with st.spinner("Scraping data securely..."):
        try:
            data = asyncio.run(scrape_zillow(url))
            df = pd.DataFrame(data)
            st.write(df)
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="zillow_listings.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Scraping failed: {str(e)}")
