# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 13:13:33 2017

@author: Serena
"""

import pandas as pd
import numpy as np
import pickle
import re
import csv
from time import sleep # So we don't request too much from the server
from collections import Counter # Keep track of counts
from selenium import webdriver
from selenium.webdriver.common import action_chains, keys
from selenium.common.exceptions import NoSuchElementException
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:

        return pickle.load(f)    

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

'''
Initialize Chrome Driver
'''
def initialize_browser():

    my_options = webdriver.ChromeOptions()
    driver_path = "C:/Data/chromedriver.exe"
    my_options.add_argument("--disable-extensions")
    my_options.add_argument("--profile-directory=Default")
    my_options.add_argument("--incognito")
    my_options.add_argument("--disable-plugins-discovery")
    my_options.add_argument("--start-maximized")
    my_options.add_argument("--disable-notifications")
    browser = webdriver.Chrome(executable_path = driver_path, chrome_options = my_options)

    return browser

def get_pause():
    return  np.random.choice(range(4,6)) 

'''
Get jobs by scraping with Chrome Driver
Returns: 
    job_dict: dict with job ID as keys, link to job as value
    job_desc: dict with job ID as keys, job description as value
'''
def search_jobs(job_name, city, job_dict, desc_dict, num_pages):
    
    browser = initialize_browser()
    browser.get("https://www.glassdoor.ca/index.htm")
    job = browser.find_element_by_id("KeywordSearch") # Get job field for job input
    location = browser.find_element_by_id("LocationSearch") # Get location field for location input
    sleep(3) # to not overwhelm the server
    job.send_keys(job_name) # look for the specific job name in the search bar
    sleep(2)
    browser.execute_script("arguments[0].value = ''", location)
    location.send_keys(city) # look for the specific city
    sleep(2)
    browser.find_element_by_xpath("//*[@id='HeroSearchButton']").click() # Click search
    # Set up initial page
    initial_url = browser.current_url
    
    for i in range(num_pages): # Get first num_pages pages 

        try:
            # Extract useful classes
            job_postings = browser.find_elements_by_class_name('jl')
            sleep(get_pause())
            for element in job_postings:
                j_id = element.get_attribute("data-id") # job_id
                link_element = element.find_element_by_css_selector('a')
                link = link_element.get_attribute('href') #job_link
                element.find_element_by_class_name("jobLink").click() # Click onto JD to expand
                sleep(2) # The key was to wait for it to load, yay!
                desc = browser.find_element_by_css_selector("#JobDesc" + j_id + " > div").text # Get description
                try:
                    job_title = browser.find_element_by_css_selector("div.empInfo.tbl").text
                    company = browser.find_element_by_class_name("empDetailsLink").text
                    if j_id not in job_dict.keys():
                        desc_dict[j_id] = desc  # To work directly with this dict
                        job_dict[j_id] = [job_title, company, city, link]
                except:
                    pass
                    
        except Exception as e:
            print(e)   
            
        try:    
            browser.find_element_by_class_name('next').click()
        except:
            pass
        browser.close()    
                
    return job_dict, desc_dict

'''
Remove "easy" "apply" "save" etc from job title
'''
def clean_job_text(job_title, words):
    for word in words:
        job_title = job_title.replace(word, "")
    return job_title 

'''
Clean up text
Input: Description from desc_dict
Output: Cleaned text
'''
def text_cleaner(text_temp):
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words("english"))
    text = text_temp.strip("\n") # break into lines    
    text = re.sub("[^a-zA-Z.+3]"," ", text)  # Now get rid of any terms that aren't words (include 3 for d3.js)
                                             # Also include + for C++    
    text = text.lower()  # Go to lower case   
    text = text.split()  #  and split them apart        
    text = [w for w in text if not w in stopwords]                    
    return text 

from nltk.corpus import stopwords
cachedStopWords = stopwords.words("english")

def text_cleaner(text_temp):
    text = text_temp.lower()
    text = re.sub("[^a-zA-Z.+3]"," ", text)
    text = text.strip("\n")
    text = ' '.join([word for word in text.split() if word not in cachedStopWords])
    return text

''' 
Input a cv and a job
Job_dict should be j_id key, then description
For key,value in job_dict.items():
    sim[key] = get_sim(cv, value, item) etc
Returns cosine tfid similarity
'''
def get_sim(cv, job_desc):    
    sim_vec = TfidfVectorizer(min_df=1)
    tfidf = sim_vec.fit_transform([cv, job_desc]) #tfidf vectorization
    sim_array = (tfidf * tfidf.T).A # cosine similarity
    sim = sim_array[0][1]
    return sim 

'''
Input cv, and all jobs in the dictionary
Return a sorted list of tuples (job_id, similarity)
'''  
def best_match(cv, d_dict):
    cv_cleaned = text_cleaner(cv)
    sim = {}
    new_desc_dict = clean_dict(d_dict)
    for key, value in new_desc_dict.items():
        #desc = text_cleaner(value)
        sim[key] = get_sim(cv_cleaned, value)
        
    best_match_dict = sorted(sim.items(), key=lambda x:x[1], reverse = True)
    return best_match_dict
      
def clean_dict(d_dict):
    new_dict = {}
    for key, value in d_dict.items():
        new_dict[key] = text_cleaner(value)
    return new_dict

'''
Input the sorted list of tuples (job_id, similarity), and
the job_dict containing the job info
Output a dict with the top x job matches
'''
def get_best(job_dict, match_list, num_jobs):    
    best_matches = {}
    for i in range(num_jobs):
        j_id = match_list[i][0]
        best_matches[j_id] = job_dict[j_id]
    best_match_df = pd.DataFrame.from_dict(best_matches, orient = "index")
    best_match_df.columns = ["Title", "Company", "Location","Link"]
    return best_match_df

def get_best_csv(cv):
    
    try:
        job_dict = load_obj("C:/Data/Projects/Glassdoor/job_dict")
        desc_dict = load_obj("C:/Data/Projects/Glassdoor/desc_dict")
    except:
        print("No dictionaries have been found!")
    
    match_list = best_match(cv, desc_dict)
    num_jobs = len(job_dict)
    best_matches = {}
    for i in range(num_jobs):
        j_id = match_list[i][0]
        best_matches[j_id] = job_dict[j_id]
    best_match_df = pd.DataFrame.from_dict(best_matches, orient = "index")
    best_match_df.columns = ["Title", "Company", "Location","Link"]
    best_match_df['Title'] = best_match_df['Title'].apply(lambda x: clean_job_text(x, ["Apply","Save","Now","Easy"]))
    path = "C:/Data/Projects/Glassdoor"
    return best_match_df.to_csv(path + "/best_match_df.csv")

