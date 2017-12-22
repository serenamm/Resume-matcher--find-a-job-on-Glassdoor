# -*- coding: utf-8 -*-
"""
Created on Sun Dec 17 09:50:21 2017

@author: Serena
"""

def scrapeGlassdoor():
    import helper

	# Load existing dictionary
	# Initialize if empty
    try:
        job_dict = load_obj("C:/Users/Serena/Desktop/Projects/Glassdoor/job_dict")
        desc_dict = load_obj("C:/Users/Serena/Desktop/Projects/Glassdoor/desc_dict")
    except:
        job_dict = {}
        desc_dict = {}
        
	# Initialize website, city, jobs
    job_lst = ["Data Analyst", "Data Scientist"]
    city_lst = ["Toronto", "Vancouver"]

	# Search for jobs
    for job_name in job_lst:
        for city in city_lst:
            
            try:
                update_jdict, update_ddict = search_jobs(job_name, city, job_dict, desc_dict, num_pages = 1)
                job_dict.update(update_jdict)
                desc_dict.update(update_ddict)
            except Exception as e:
                print(e)
                
    save_obj(job_dict, "job_dict")
    save_obj(desc_dict, "desc_dict")
