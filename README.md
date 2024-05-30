# Flipkart Product Reviews Scraper

## Overview
This Python script fetches Flipkart product reviews details including title, text, rating, user name, user address, review likes, review dislikes, and review date.

## How to Use
1. **Installation**: Ensure you have Python installed on your system. This script uses the following libraries:
   - `requests`
   - `re`
   - `math`
   - `json`
   - `BeautifulSoup` (from `bs4`)
   - `urlparse` and `urlencode` (from `urllib.parse`)
   - `ThreadPoolExecutor` and `as_completed` (from `concurrent.futures`)
   Ensure these libraries are installed before running the script.

2. **Execution**: Run the `scrape.py` script in your Python environment. You'll be prompted to enter the product URL. The script will then fetch all reviews associated with that product.

3. **Output**: The script outputs the reviews in JSON format, including the title, text, rating, user name, user address, review likes, review dislikes, and review date.

## Additional Information
- **Performance**: Note that `scrape.py` is faster compared to `scrape2.py`.
- **Concurrent Processing**: The script utilizes concurrent processing to fetch reviews from multiple pages simultaneously, enhancing efficiency.

## Note
Ensure the product URL provided is valid and corresponds to a product on Flipkart's website.

## Disclaimer
This script is intended for educational and informational purposes only. Use it responsibly and respect the terms of service of the website being scraped.

Happy scraping! 🚀
