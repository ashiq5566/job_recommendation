from django.shortcuts import render, redirect
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import nltk
nltk.data.path.append("/home/ashiq/nltk_data")
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from bs4 import BeautifulSoup

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

        # Remove stop words (common words that don't add meaning)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if not word in stop_words]

        # Define a list of Python-related keywords
        python_keywords = ['python', 'pytorch', 'sql', 'mxnet', 'mlflow', 'einstein', 'theano', 'pyspark', 'solr', 'mahout', 
        'cassandra', 'aws', 'powerpoint', 'spark', 'pig', 'sas', 'java', 'nosql', 'docker', 'salesforce', 'scala', 'r',
        'c', 'c++', 'net', 'tableau', 'pandas', 'scikitlearn', 'sklearn', 'matlab', 'scala', 'keras', 'tensorflow', 'clojure',
        'caffe', 'scipy', 'numpy', 'matplotlib', 'vba', 'spss', 'linux', 'azure', 'cloud', 'gcp', 'mongodb', 'mysql', 'oracle', 
        'redshift', 'snowflake', 'kafka', 'javascript', 'qlik', 'jupyter', 'perl', 'bigquery', 'unix', 'react',
        'scikit', 'powerbi', 's3', 'ec2', 'lambda', 'ssrs', 'kubernetes', 'hana', 'spacy', 'tf', 'django', 'sagemaker',
        'seaborn', 'mllib', 'github', 'git', 'elasticsearch', 'splunk', 'airflow', 'looker', 'rapidminer', 'birt', 'pentaho', 
        'jquery', 'nodejs', 'd3', 'plotly', 'bokeh', 'xgboost', 'rstudio', 'shiny', 'dash', 'h20', 'h2o', 'hadoop', 'mapreduce', 
        'hive', 'cognos', 'angular', 'nltk', 'flask', 'node', 'firebase', 'bigtable', 'rust', 'php', 'cntk', 'lightgbm', 
        'kubeflow', 'rpython', 'unixlinux', 'postgressql', 'postgresql', 'postgres', 'hbase', 'dask', 'ruby', 'julia', 'tensor',
        # added r packages doesn't seem to impact the result
        'dplyr','ggplot2','esquisse','bioconductor','shiny','lubridate','knitr','mlr','quanteda','dt','rcrawler','caret','rmarkdown',
        'leaflet','janitor','ggvis','plotly','rcharts','rbokeh','broom','stringr','magrittr','slidify','rvest',
        'rmysql','rsqlite','prophet','glmnet','text2vec','snowballc','quantmod','rstan','swirl','datasciencer']

        # Find keywords in the filtered words
        found_keywords = [word for word in filtered_words if word in python_keywords]
        keywords = "+".join(found_keywords)
        print(found_keywords)
        # Get user input for job location
        location = loc
        return redirect('result', location=location, keywords=keywords)
    context = {
        'keywords':keywords,
        'location':location
    }
    return render(request,'index.html', context)

def result(request, location, keywords):
    # Configure Selenium to use Chrome driver
    driver = webdriver.Chrome()

    url = f"https://in.indeed.com/jobs?q={keywords}&l={location}"

    # Open URL in Selenium-controlled Chrome browser
    driver.get(url)

    # Wait for page to load
    driver.implicitly_wait(10)

    # Scroll down to load more job listings
    for i in range(5):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        driver.implicitly_wait(2)

    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    job_information = []

    # Find all job listings on the page
    job_listings = soup.find_all(class_="tapItem")

    # Print the title, company, and location for each job listing
    for job in job_listings:
        try:
            title = job.find(class_=["jobTitle"]).text.strip()
            company = job.find(class_="companyName").text.strip()
            location_elem = job.find(class_="companyLocation")
            location = location_elem.text.strip() if location_elem else "N/A"
            link_elem = job.find("a", class_="jcs-JobTitle")
            link = link_elem["data-jk"] if link_elem else None
            print(f"Title: {title}\nCompany: {company}\nLocation: {location}\n")
            job_information.append({
                "title": title,
                "company": company,
                "location": location,
                'link':link
                
            })
        except AttributeError:
            print("Error: could not find job information")
    #Close the Selenium-controlled browser
    driver.quit()
    context = {
        'job_information':job_information
    }
    return render(request,'result.html', context)

# Build URL for job search with keywords and location
        



