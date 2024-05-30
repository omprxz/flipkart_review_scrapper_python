import requests
import re
import json
import math
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import time

start=time.time()
allReviews = []

def extractReviewDetailsToJson(html):
    allR = []
    rv = BeautifulSoup(html, 'html.parser')
    sno = 1
    
    reviews = rv.find_all(class_="cPHDOP")[4:-1]
    for review in reviews:
        title_element = review.find(class_="z9E0IG")
        title = title_element.get_text().strip() if title_element else ""
        
        rating_element = review.find(class_="XQDdHH")
        rating = rating_element.get_text().strip() if rating_element else ""
        
        content_element = review.find(class_="ZmyHeo")
        content = content_element.get_text().strip().replace("READ MORE", "") if content_element else ""
        
        if content_element and content_element.find(class_="XQDdHH"):
            content = content[1:]
        
        user_name_element = review.find(class_="_2NsDsF")
        user_name = user_name_element.get_text().strip() if user_name_element else ""
        
        user_address_element = review.select_one(".MztJPv > span:nth-of-type(2)")
        user_address = user_address_element.get_text().strip().replace(",", "") if user_address_element else ""
        
        days_ago_element = review.find_all(class_="_2NsDsF")
        days_ago = days_ago_element[-1].get_text().strip() if days_ago_element else ""
        
        likes_element = review.select(".qhmk-f .tl9VpF")
        likes = likes_element[0].get_text().strip() if likes_element else ""
        
        dislikes_element = review.select(".qhmk-f .tl9VpF")
        dislikes = dislikes_element[-1].get_text().strip() if dislikes_element else ""

        if rating and content and user_name and days_ago:
            allR.append({
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
            sno += 1

    return allR

def emptyOrInvalidLink(link):
    if link == '':
        print('Provide with product link')
        link = input('Enter product url: ')
        emptyOrInvalidLink(link)

def product2reviewLink(link, page=None):
    url_obj = urlparse(link)
    pathname = url_obj.path
    search_params = parse_qs(url_obj.query)
    search_params.pop("spotlightTagId", None)
    search_params.pop("q", None)
    search_params.pop("pageUID", None)
    
    if page is not None:
        search_params["page"] = [page]
    
    new_pathname = pathname.replace("/p/", "/product-reviews/")
    new_query = urlencode(search_params, doseq=True)
    new_url = urlunparse((url_obj.scheme, url_obj.netloc, new_pathname, url_obj.params, new_query, url_obj.fragment))
    return new_url

def fetchReviewsDetails(link):
    global allReviews
    response = requests.get(link)
    print('Please wait while all reviews being scraped...')
    if response.status_code == 200:
        htmlResp = response.text
        soup = BeautifulSoup(htmlResp, 'html.parser')
        pattern = r'(\d{1,3}(,\d{3})*|\d{1,3})(\.\d+)?(\s+r(ating|eview)s?)'
        match = re.search(pattern, htmlResp, re.IGNORECASE)
        totalReviews = 0
        if match:
            totalReviews = int(match.group(1).replace(',', ''))
            if totalReviews == 0:
                print('No reviews')
                return
            
        totalPages = math.ceil(totalReviews/10)
        allReviews.extend(extractReviewDetailsToJson(htmlResp))
        for i in range(2, totalPages+1):
            rvLink = product2reviewLink(reviewLink, i)
            response = requests.get(rvLink)
            if response.status_code == 200:
                htmlResp = response.text
                allReviews.extend(extractReviewDetailsToJson(htmlResp))
        print('\n',json.dumps(allReviews, indent=4))

link = input('Enter product url: ')
if link == '':
    emptyOrInvalidLink(link)

reviewLink = product2reviewLink(link)
fetchReviewsDetails(reviewLink)

end=time.time()

print('\nScrapped in',end=' ')
print(round(end - start),end='')
print('s')