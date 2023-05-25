from django.shortcuts import render, redirect
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import nltk
nltk.data.path.append("/home/ashiq/nltk_data")
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .models import KeywordList
import string




# Create your views here.
def job(request):
    keywords = ''  # Initialize the variable with an empty string
    location = ''
    if request.method=="POST":
        desc = request.POST.get('job1')
        loc = request.POST.get('loc')
    
        # Get user input for job description
        description = desc
        print(description)

        # Tokenize the description into words
        words = word_tokenize(description)
        words = [word.lower() for word in words]
        print("after tokenisation",words)


        
        # Remove stop words (common words that don't add meaning)
        stop_words = set(stopwords.words('english'))
        def is_named_entity(word):
            tagged_words = pos_tag(word_tokenize(word))
            tree = ne_chunk(tagged_words)
            for subtree in tree:
                if isinstance(subtree, Tree) and subtree.label() != 'S':
                    return True
            return False
        
        # Remove punctuation marks from words
        words = [word for word in words if word not in string.punctuation]

        # filtered_words = [word for word in words if not word in stop_words]
        filtered_words = [word.lower() for word in words if word.lower() not in stop_words and not is_named_entity(word)]
        print("words after fitering",filtered_words)

        # Find keywords in the filtered words
        # found_keywords = [word for word in filtered_words if word in job_keywords]
        # keywords = "+".join(found_keywords)
        # print(found_keywords)
        # Get user input for job location
        location = loc
        
        keyword_list = KeywordList.objects.first()
        if keyword_list:
            job_keywords = keyword_list.keywords.split(',')
        else:
            job_keywords = []
        
        new_keywords = [word for word in filtered_words if word not in job_keywords]
        print("new words to be added",new_keywords)
        if new_keywords:
            # Append the new keywords to the existing keyword list
            job_keywords += new_keywords
            found_keywords = [word for word in filtered_words if word in job_keywords]
            keywords = "+".join(found_keywords)
        else:
            found_keywords = [word for word in filtered_words if word in job_keywords]
            keywords = "+".join(found_keywords)
        print("current keyword List",keywords)
        
        if keyword_list:
            # If a keyword list exists, update it
            keyword_list.keywords = ','.join(job_keywords)
            keyword_list.save()
        else:
            # If no keyword list exists, create a new one
            KeywordList.objects.create(keywords=','.join(job_keywords))
        
        keywords = "+".join(found_keywords)
        
        return redirect('result', location=location, keywords=keywords)
    context = {
        'keywords':keywords,
        'location':location
    }
    return render(request,'index.html', context)


def result(request, location, keywords):
    
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    
    # Configure Selenium to use Chrome driver
    driver = webdriver.Chrome()

    # List of sites to scrape
    sites = [
        {
            'name': 'Indeed',
            'url': f"https://in.indeed.com/jobs?q={keywords}&l={location}",
            'listing_class': 'tapItem',
            'title_class': 'jobTitle',
            'company_class': 'companyName',
            'location_class': 'companyLocation',
            'link_class': 'jcs-JobTitle'
        },
        {
            'name': 'Naukri',
            'url': f"https://www.naukri.com/{keywords}-jobs-in-{location}?k={keywords}&l={location}",
            'listing_class': 'jobTuple',
            'title_class': 'title',
            'company_class': 'subTitle',
            'location_class': 'locWdth',
            'link_class': 'title'
        },
        {
            'name': 'Monster',
            'url': f"https://www.monster.com/jobs/search?q={keywords}&where={location}",
            'listing_class': 'sc-iJCbQK',
            'title_class': 'sc-czvZiG',
            'company_class': 'sc-bQFuvY',
            'location_class': 'sc-bOtlzW',
            'link_class': 'sc-jHwEXd'
        },
        {
            'name': 'LinkedIn',
            'url': f"https://www.linkedin.com/jobs/search?keywords={keywords}&location={location}",
            'listing_class': 'jobs-search__results-list',
            'title_class': 'base-search-card__title',
            'company_class': 'base-search-card__subtitle',
            'location_class': 'job-search-card__location',
            'link_class': 'base-card__full-link'
        },
        # Add more sites as needed
    ]
    job_information = []

    for site in sites:
        # Open URL in Selenium-controlled Chrome browser
        driver.get(site['url'])

        # Wait for page to load
        driver.implicitly_wait(20)

        # Scroll down to load more job listings
        for i in range(10):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            driver.implicitly_wait(2)

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Find all job listings on the page
        job_listings = soup.find_all(class_=site['listing_class'])

        # Print the title, company, and location for each job listing
        for job in job_listings:
            try:
                title = job.find(class_=site['title_class']).text.strip()
                company = job.find(class_=site['company_class']).text.strip()
                location_elem = job.find(class_=site['location_class'])
                location = location_elem.text.strip() if location_elem else "N/A"
                link_elem = job.find("a", class_=site['link_class'])
                link = urljoin(site['url'], link_elem["href"]) if link_elem else None
                print(f"Site: {site['name']}")
                print(f"Title: {title}\nCompany: {company}\nLocation: {location}\nlink: {link}")
                job_information.append({
                    "site": site['name'],
                    "title": title,
                    "company": company,
                    "location": location,
                    'link': link
                })
            except AttributeError:
                print(f"Error: could not find job information on {site['name']}")

    # Close the Selenium-controlled browser
    driver.quit()
    context = {
        'job_information': job_information
    }
    return render(request, 'result.html', context)
        



