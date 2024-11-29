import requests
from bs4 import BeautifulSoup

def fetch_article_data(article_url, skip_paragraphs):

    response = requests.get(article_url)
    if response.status_code != 200:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return "", ""
    
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
    article_body = soup.find_all('p')
    if skip_paragraphs == 0:
        article_content = " ".join([paragraph.get_text(strip=True) for paragraph in article_body])
    else:
        article_content = " ".join([paragraph.get_text(strip=True) for paragraph in article_body[:-skip_paragraphs]])
    
    return title, article_content


def political(article_url):
    if "bbc.com" in article_url:
        return fetch_article_data(article_url, 7)

    elif any(domain in article_url for domain in ["politico.com", "aljazeera.com", "news.sky.com", "theguardian.com"]):
        return fetch_article_data(article_url, 0)

    elif any(domain in article_url for domain in ["dw.com", "cnn.com"]):
        return fetch_article_data(article_url, 1)

    elif "newindianexpress.com" in article_url:
        return fetch_article_data(article_url, 5)

    else:
        return "", ""

def sports(article_url):
    if "skysports.com" in article_url or "90min.com" in article_url:
        return fetch_article_data(article_url, 2)

    elif "bbc.com" in article_url:
        return fetch_article_data(article_url, 7)

    elif "theguardian.com" in article_url:
        return fetch_article_data(article_url, 0)

    elif "sports.ndtv.com" in article_url:
        return fetch_article_data(article_url, 5)

    elif "si.com" in article_url:
        return fetch_article_data(article_url, 3)

    else:
        return "", ""

def money(article_url):
    if "moneycontrol.com" in article_url or "livemint.com" in article_url:
        return fetch_article_data(article_url, 3)

    elif "thisismoney.co.uk" in article_url:
        return fetch_article_data(article_url)

    elif "finshots.in" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "Don't forget to share" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    else:
        return "", ""

def tech_science(article_url):
    if "bbc.com" in article_url:
        return fetch_article_data(article_url, 7)

    elif "abcnews.go.com" in article_url:
        return fetch_article_data(article_url, 1)

    elif "discovermagazine.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "Read More" in paragraph.get_text(strip=True):
                continue
            if "Our writers atDiscovermagazine.com" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    elif "sciencenews.org" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "Questions or comments" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    else:
        return "", ""

def med_health(article_url):
    if "bbc.com" in article_url:
        return fetch_article_data(article_url, 7)

    elif "clinicaladvisor.com" in article_url:
        return fetch_article_data(article_url, 6)

    elif "kffhealthnews.org" in article_url:
        return fetch_article_data(article_url, 13)

    elif any(domain in article_url for domain in ["abcnews.go.com", "cnn.com","livescience.com"]):
        return fetch_article_data(article_url, 1)

    elif "discovermagazine.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "Read More" in paragraph.get_text(strip=True):
                continue
            if "Our writers atDiscovermagazine.com" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    elif "medscape.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "Send comments" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    elif "medicalnewstoday.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "Share this article" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    elif "mobihealthnews.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h2').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        article_content = " ".join([paragraph.get_text(strip=True) for paragraph in article_body[:-8]])
        return title, article_content

    else:
        return "", ""

def entertainment(article_url):

    if any(domain in article_url for domain in ["variety.com", "vulture.com"]):
        return fetch_article_data(article_url, 2)

    elif "indiewire.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "By providing your information" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    elif "deadline.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "Get our Breaking News" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    elif "vibe.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "—" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    else:
        return "", ""

def nature_environment(article_url):

    if any(domain in article_url for domain in ["grist.org","nature.com"]):
        return fetch_article_data(article_url, 0)

    if any(domain in article_url for domain in ["enn.com", "loe.org"]):
        return fetch_article_data(article_url, 2)

    else:
        return "", ""

def crime_law(article_url):

    if any(domain in article_url for domain in ["livelaw.in","cbsnews.com","barandbench.com"]):
        return fetch_article_data(article_url, 0)

    elif "lawandcrime.com" in article_url:
        response = requests.get(article_url)
        if response.status_code != 200:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return "", ""
        
        soup = BeautifulSoup(response.content, "html.parser")
        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No title found"
        article_body = soup.find_all('p')
        
        article_content = []
        for paragraph in article_body:
            if "Have a tip" in paragraph.get_text(strip=True):
                break
            article_content.append(paragraph.get_text(strip=True))

        article_content = " ".join(article_content)
        return title, article_content

    else:
        return "", ""

def ai_crpyto_data_blockchain(article_url):

    if any(domain in article_url for domain in ["analyticsinsight.net"]):
        return fetch_article_data(article_url, 2)

    elif any(domain in article_url for domain in ["bigdatawire.com"]):
        return fetch_article_data(article_url, 3)


    elif any(domain in article_url for domain in ["dataversity.net","dataconomy.com","dlabs.ai"]):
        return fetch_article_data(article_url, 1)

    else:
        return "", ""