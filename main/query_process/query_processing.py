from web_scraping.scraper import WebScraper
from relevance_check.relevance_model import RelevanceModel
from storage.database import PostgresDB
from concurrent.futures import ThreadPoolExecutor, as_completed

class ProcessSystem:
    def __init__(self):
        # retrive the necessary modules
        self.scraper = WebScraper()
        self.relevance_model = RelevanceModel()
        self.db = PostgresDB()

    def process_query(self, query, engine, scrape_type, advanced_scrape):
        # stores the query in database and scrapes the article via scraper module. Sends the articles to relevance module for further actions. 
        query_id = self.db.store_query(query,engine, scrape_type, advanced_scrape)

        if engine == 'Google':
            if scrape_type == 'Full': # scrape
                if advanced_scrape == 'Yes': # :site
                    url_list,category = self.scraper.google_search_full_advanced_scrape(query)

                    scraped_articles = []

                    max_workers = min(10, len(url_list))
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        future_to_url = {
                            executor.submit(self.scraper.site_specific_scrape, url, category): url for url in url_list
                        }

                        for future in as_completed(future_to_url):
                            url = future_to_url[future]
                            try:
                                title, content = future.result()
                            except Exception as e:
                                print(f"Error scraping {url}: {e}")
                                title, content = "N/A", "N/A"  # Default values in case of failure
                            scraped_articles.append({"url": url, "title": title, "content": content})

                    query_embedding = self.relevance_model.embed_text(query)
                    print("query_embedding generated")
                    relevant_chunks, collection_name = self.relevance_model.check_relevance(query_id,query,scraped_articles, query_embedding)

                    if len(relevant_chunks) > 0:
                        print(f"Processed {len(relevant_chunks)} relevant chunks for the query: {query}")
                        return collection_name

                    else:
                        print("No relevant data found for the query")
                        return None
                else:
                    url_list = self.scraper.google_search_full_no_advanced_scrape(query)

                    scraped_articles = []

                    max_workers = min(10, len(url_list))
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        future_to_url = {
                            executor.submit(self.scraper.non_site_specific_scrape, url): url for url in url_list
                        }

                        for future in as_completed(future_to_url):
                            url = future_to_url[future]
                            try:
                                title, content = future.result()
                            except Exception as e:
                                print(f"Error scraping {url}: {e}")
                                title, content = "N/A", "N/A"  # Default values in case of failure
                            scraped_articles.append({"url": url, "title": title, "content": content})

                    query_embedding = self.relevance_model.embed_text(query)
                    print("query_embedding generated")
                    relevant_chunks, collection_name = self.relevance_model.check_relevance(query_id,query,scraped_articles, query_embedding)

                    if len(relevant_chunks) > 0:
                        print(f"Processed {len(relevant_chunks)} relevant chunks for the query: {query}")
                        return collection_name

                    else:
                        print("No relevant data found for the query")
                        return None
            else: # snippet
                if advanced_scrape == 'Yes': # :site
                    scraped_articles = self.scraper.google_search_snippet_advanced_scrape(query)

                    query_embedding = self.relevance_model.embed_text(query)
                    print("query_embedding generated")
                    relevant_chunks, collection_name = self.relevance_model.check_relevance(query_id,query,scraped_articles, query_embedding)

                    if len(relevant_chunks) > 0:
                        print(f"Processed {len(relevant_chunks)} relevant chunks for the query: {query}")
                        return collection_name

                    else:
                        print("No relevant data found for the query")
                        return None
                else: # normal
                    scraped_articles = self.scraper.google_search_snippet_non_advanced_scrape(query)

                    query_embedding = self.relevance_model.embed_text(query)
                    print("query_embedding generated")
                    relevant_chunks, collection_name = self.relevance_model.check_relevance(query_id,query,scraped_articles, query_embedding)

                    if len(relevant_chunks) > 0:
                        print(f"Processed {len(relevant_chunks)} relevant chunks for the query: {query}")
                        return collection_name

                    else:
                        print("No relevant data found for the query")
                        return None
        else: #duckduckgo
            if scrape_type == 'Full': # scrape
                    url_list = self.scraper.duckduckgo_full(query)

                    scraped_articles = []

                    max_workers = min(10, len(url_list))
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        future_to_url = {
                            executor.submit(self.scraper.non_site_specific_scrape, url): url for url in url_list
                        }

                        for future in as_completed(future_to_url):
                            url = future_to_url[future]
                            try:
                                title, content = future.result()
                            except Exception as e:
                                print(f"Error scraping {url}: {e}")
                                title, content = "N/A", "N/A"  # Default values in case of failure
                            scraped_articles.append({"url": url, "title": title, "content": content})

                    query_embedding = self.relevance_model.embed_text(query)
                    print("query_embedding generated")
                    relevant_chunks, collection_name = self.relevance_model.check_relevance(query_id,query,scraped_articles, query_embedding)

                    if len(relevant_chunks) > 0:
                        print(f"Processed {len(relevant_chunks)} relevant chunks for the query: {query}")
                        return collection_name

                    else:
                        print("No relevant data found for the query")
                        return None
            else: # snippet
                    scraped_articles = self.scraper.duckduckgo_snippet(query)

                    query_embedding = self.relevance_model.embed_text(query)
                    print("query_embedding generated")
                    relevant_chunks, collection_name = self.relevance_model.check_relevance(query_id,query,scraped_articles, query_embedding)

                    if len(relevant_chunks) > 0:
                        print(f"Processed {len(relevant_chunks)} relevant chunks for the query: {query}")
                        return collection_name

                    else:
                        print("No relevant data found for the query")
                        return None
