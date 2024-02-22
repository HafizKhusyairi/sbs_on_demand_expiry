from playwright.sync_api import Playwright, sync_playwright, expect
from bs4 import BeautifulSoup
import pandas as pd
import os

# Put your username and  password here
username = ""
password = ""

# Function to parse all the links in favourites
def parse_link(html_page):
    soup = BeautifulSoup(html_page, features="html.parser")
    parsed = []
    for item in soup.find_all('a'):
        link = item.get('href')
        if 'movie/' in link:
            parsed.append(link)
    return parsed

# Function to parse title and expiry information from each movie page
def parse_expiry(html_page):
    soup = BeautifulSoup(html_page, features="html.parser")
    expiry = [text for text in soup.stripped_strings if 'Expires in ' in text]
    if len(expiry) > 0:
        parsed_expiry.append(expiry[0])
        title = [text for text in soup.stripped_strings if 'Watch ' in text]
        parsed_title.append(title[0])

# Run through all links in favourites and extract titles and expiry
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.sbs.com.au/ondemand/favourites")
    page.get_by_role("banner").get_by_role("button", name="Sign In").click()
    page.get_by_label("Email").click()
    page.get_by_label("Email").fill(username)
    page.get_by_text("Password visibility").click()
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_role("button", name="Sign In").click()
    page.wait_for_url("https://www.sbs.com.au/ondemand/favourites")
    page.wait_for_timeout(1000)
    if page.get_by_role("button", name = "View More"):
        page.get_by_role("button", name = "View More").click()
    page.wait_for_timeout(1000)
    film_links = parse_link(page.content())
    for link in film_links:
        page1 = context.new_page()
        page1.goto("https://www.sbs.com.au/" + link)
        page1.wait_for_timeout(1000)
        parse_expiry(page1.content())
        page1.close()
    context.close()
    browser.close()

parsed_expiry = []
parsed_title = []
with sync_playwright() as playwright:
    run(playwright)
df = pd.DataFrame({'Title': parsed_title, 'Exp': parsed_expiry})
df['Title'] = df['Title'].str.removeprefix("Watch ").str.removesuffix(" | SBS On Demand")
df.to_csv(os.path.dirname(os.path.realpath(__file__)) + "/expiry_list.csv")