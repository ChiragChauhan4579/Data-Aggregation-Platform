import ollama
from bs4 import BeautifulSoup
import requests
from googlesearch import search
from web_scraping.scraper_utils import *
from duckduckgo_search import DDGS
from concurrent.futures import ThreadPoolExecutor, as_completed

categories = {"Political":["bbc.com","politico.com","theguardian.com","aljazeera.com","dw.com","news.sky.com","edition.cnn.com","newindianexpress.com"],
              "Sports":["skysports.com","bbc.com","theguardian.com","sports.ndtv.com","90min.com","si.com"],
              "Economics / Finance / Stock / Business & Startups":["moneycontrol.com","livemint.com","thisismoney.co.uk","finshots.in"],
              "Technology and Science":["bbc.com","abcnews.go.com","sciencenews.org","discovermagazine.com"],
              "Medical and Healthcare":["bbc.com","edition.cnn.com","discovermagazine.com","abcnews.go.com","mobihealthnews.com","medscape.com","medicalnewstoday.com","clinicaladvisor.com",
                                        "kffhealthnews.org","livescience.com"],
              "Entertainment":["deadline.com","indiewire.com","variety.com","vibe.com","vulture.com"],
              "Nature, Climate and Environment":["enn.com", "loe.org","grist.org","nature.com"],
              "Crime and Law":["livelaw.in","cbsnews.com","barandbench.com","lawandcrime.com"],
              "AI & Big Data, Blockchain and crypto":["analyticsinsight.net","bigdatawire.com","dataversity.net","dataconomy.com","dlabs.ai"],
            }

def fetch_articles(site, query, max_results):
    links = search(query + f" site:{site}", num_results=max_results, advanced=True)
    articles = [{"url": link.url, "title": link.title, "content": link.description} for link in links]
    return articles

class WebScraper:
    def __init__(self):
        pass

    def get_category(self,query):

        prompt = f"""You are a categorization expert tasked with classifying input for scraping Google. You will help identify the category that best suits scraping details from relevant websites.

        Given the query below, your job is to output only the most appropriate category. Don't generate any additional text.
        query: "{query}"

        Output: Ensure the output should be from the listed categories only: [Political, Sports, Economics / Finance / Stock / Business & Startups, Technology and Science, Medical and Healthcare, Entertainment, Nature, Climate and Environment, Crime and Law, AI & Big Data, Blockchain and crypto].
        """

        response = ollama.generate(model='orca-mini:7b-q2_K', prompt=prompt)

        for key in categories.keys():
            if key.lower() in response['response'].lower():
                return key
        else:
            return "Political"

    def google_search_full_advanced_scrape(self, query, max_results=5):
        # makes google search and scrapes 5 articles per site and returns the list of articles

        category = self.get_category(query)

        category_websites = categories[category]
        print(f"Selected Category: {category}, Websites: {category_websites}")

        url_list = []
        for site in category_websites:
            links = search(query + f" site:{site}",num_results=max_results,advanced=True)
            for i in links:
                url_list.append(i.url)

        print(url_list)
        return url_list,category


    def google_search_full_no_advanced_scrape(self, query, max_results=25):
        # makes google search and scrapes 5 articles per site and returns the list of articles

        url_list = []
        links = search(query,num_results=max_results,advanced=True)
        for i in links:
            url_list.append(i.url)

        print(url_list)
        return url_list

    def google_search_snippet_advanced_scrape(self, query, max_results=5):
        # makes google search and scrapes 5 articles per site and returns the list of articles

        category = self.get_category(query)

        category_websites = categories[category]
        print(f"Selected Category: {category}, Websites: {category_websites}")

        scraped_articles = []

        with ThreadPoolExecutor() as executor:
            # Submit each site scrape task to the executor
            future_to_site = {
                executor.submit(fetch_articles, site, query, max_results): site
                for site in category_websites
            }
            
            # As tasks complete, collect the articles
            for future in as_completed(future_to_site):
                site = future_to_site[future]
                try:
                    articles = future.result()
                    scraped_articles.extend(articles)
                except Exception as exc:
                    print(f"An error occurred while scraping {site}: {exc}")

        return scraped_articles


    def google_search_snippet_non_advanced_scrape(self, query, max_results=25):
        # makes google search and scrapes 5 articles per site and returns the list of articles

        scraped_articles = []
        
        links = search(query,num_results=max_results,advanced=True)
        for i in links:
            scraped_articles.append({"url": i.url, "title": i.title, "content": i.description})

        return scraped_articles

    def duckduckgo_full(self, query, max_results=25):
        # makes google search and scrapes 5 articles per site and returns the list of articles

        url_list = []
        links = DDGS().text(query, max_results=max_results)
        for i in links:
            url_list.append(i['href'])

        print(url_list)
        return url_list

    def duckduckgo_snippet(self, query, max_results=25):
        # makes google search and scrapes 5 articles per site and returns the list of articles

        scraped_articles = []
        
        links = DDGS().text(query, max_results=max_results)
        for i in links:
            scraped_articles.append({"url": i['href'], "title": i['title'], "content": i['body']})

        return scraped_articles

    def site_specific_scrape(self, article_url,category):
        # scrapes the html of the site and returns the text content
        
        try:
            if "political" == category.lower():
                title, content = political(article_url)
            if "sports" == category.lower():
                title, content = sports(article_url)
            if "money" == category.lower():
                title, content = money(article_url)
            if "tech_science" == category.lower():
                title, content = tech_science(article_url)
            if "med_health" == category.lower():
                title, content = med_health(article_url)
            if "entertainment" == category.lower():
                title, content = entertainment(article_url)
            if "nature_environment" == category.lower():
                title, content = nature_environment(article_url)
            if "crime_law" == category.lower():
                title, content = crime_law(article_url)
            if "ai_crypto_data_blockchain" == category.lower():
                title, content = ai_crpyto_data_blockchain(article_url)

        except Exception as e:
            title, content = "Not found", "Not found"

        return title,content
    

    def non_site_specific_scrape(self, article_url,category):
        # scrapes the html of the site and returns the text content
        
        try:
            
            response = requests.get(article_url)
            if response.status_code != 200:
                print(f"Failed to retrieve data. Status code: {response.status_code}")
                return "", ""
            
            soup = BeautifulSoup(response.content, "html.parser")
            title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
            article_body = soup.find_all('p')
            content = " ".join([paragraph.get_text(strip=True) for paragraph in article_body])
            
            return title, content

        except Exception as e:
            title, content = "Not found", "Not found"
            return title,content