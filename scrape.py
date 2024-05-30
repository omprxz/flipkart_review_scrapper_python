import requests
import re
import math
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

start_time = time.time()
allReviews = []

def extractReviewDetailsToJson(html):
    rv = BeautifulSoup(html, 'html.parser')
    reviews = rv.find_all(class_="cPHDOP")[4:-1]

    extracted_reviews = []
    for sno, review in enumerate(reviews, start=1):
        title = review.find(class_="z9E0IG").get_text(strip=True) if review.find(class_="z9E0IG") else ""
        rating = review.find(class_="XQDdHH").get_text(strip=True) if review.find(class_="XQDdHH") else ""
        content_element = review.find(class_="ZmyHeo")
        content = content_element.get_text(strip=True).replace("READ MORE", "") if content_element else ""
        if content_element and content_element.find(class_="XQDdHH"):
            content = content[1:]
        user_name = review.find(class_="_2NsDsF").get_text(strip=True) if review.find(class_="_2NsDsF") else ""
        user_address = review.select_one(".MztJPv > span:nth-of-type(2)").get_text(strip=True).replace(",", "") if review.select_one(".MztJPv > span:nth-of-type(2)") else ""
        days_ago = review.find_all(class_="_2NsDsF")[-1].get_text(strip=True) if review.find_all(class_="_2NsDsF") else ""
        likes = review.select(".qhmk-f .tl9VpF")[0].get_text(strip=True) if review.select(".qhmk-f .tl9VpF") else ""
        dislikes = review.select(".qhmk-f .tl9VpF")[-1].get_text(strip=True) if review.select(".qhmk-f .tl9VpF") else ""

        if rating and content and user_name and days_ago:
            extracted_reviews.append({
                "sno": sno,
                "title": title,
                "rating": rating,
                "content": content,
                "userName": user_name,
                "userAddress": user_address,
                "daysAgo": days_ago,
                "likes": likes,
                "dislikes": dislikes
            })

    return extracted_reviews

def emptyOrInvalidLink(link):
    while not link:
        print('Provide a product link')
        link = input('Enter product url: ')

def product2reviewLink(link, page=None):
    url_obj = urlparse(link)
    search_params = parse_qs(url_obj.query)
    search_params.pop("spotlightTagId", None)
    search_params.pop("q", None)
    search_params.pop("pageUID", None)
    
    if page is not None:
        search_params["page"] = [page]
    
    new_pathname = url_obj.path.replace("/p/", "/product-reviews/")
    new_query = urlencode(search_params, doseq=True)
    new_url = urlunparse((url_obj.scheme, url_obj.netloc, new_pathname, url_obj.params, new_query, url_obj.fragment))
    return new_url

def fetchPageReviews(link, page):
    rvLink = product2reviewLink(link, page)
    response = requests.get(rvLink)
    if response.status_code == 200:
        htmlResp = response.text
        return extractReviewDetailsToJson(htmlResp)
    return []

def fetchReviewsDetails(link):
    global allReviews
    response = requests.get(link)
    print('Please wait while all reviews are being scraped...')
    if response.status_code == 200:
        htmlResp = response.text
        pattern = r'(\d{1,3}(,\d{3})*|\d{1,3})(\.\d+)?(\s+r(ating|eview)s?)'
        match = re.search(pattern, htmlResp, re.IGNORECASE)
        
        totalReviews = int(match.group(1).replace(',', '')) if match else 0
        if totalReviews == 0:
            print('No reviews')
            return
        
        totalPages = math.ceil(totalReviews / 10)
        allReviews.extend(extractReviewDetailsToJson(htmlResp))
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(fetchPageReviews, link, i) for i in range(2, totalPages + 1)]
            for future in as_completed(futures):
                allReviews.extend(future.result())
        
        print('\n',json.dumps(allReviews, indent=4))

link = input('Enter product url: ')
emptyOrInvalidLink(link)

reviewLink = product2reviewLink(link)
fetchReviewsDetails(reviewLink)

print('\nScrapped in',end=' ')
print(round(time.time() - start_time),end='')
print('s')