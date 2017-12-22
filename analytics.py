# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 13:06:53 2017

@author: Serena
"""

def get_analytics():    
    """
    Created on Tue Aug 16 22:48:18 2016
    
    @author: Diego
    """
    import pandas as pd
    from collections import Counter # Keep track of our term counts
    from helperP3 import load_obj, skills_info
    
    try:               
        jobDict = load_obj('glassDoorDict')
    except:
        return 'No dictionary found in the folder'
    
    completeDict = dict(filter(lambda x,: len(x[1]) == 6, jobDict.items()))   
        
    finalDict = dict(map(lambda (x,y): (x, y[0:5] + [skills_info([y[0]]+y[5])]), completeDict.items()))
    
     
    # Calculate top locations  

    location_dict = Counter()
    location_dict.update([finalDict[item][3] for item in finalDict.keys()])    
    location_frame = pd.DataFrame(location_dict.items(), columns = ['Term', 'NumPostings'])
    
    # Calculate top companies - (company, rating) , Num posting
    
    company_dict = Counter()
    company_dict.update([(finalDict[item][2],finalDict[item][1]) for item in finalDict.keys()])
    company_frame = pd.DataFrame(company_dict.items(), columns = ['Term', 'NumPostings'])
        
    # Calculate other analytics
    skill_frame, edu_frame, lang_frame = skills_info(completeDict)    
    
    return location_frame, company_frame, skill_frame, edu_frame, lang_frame

def getWordCloud(skill_frame):
    from wordcloud import WordCloud
    from scipy.misc import imread
    import matplotlib.pyplot as plt
    
    words = zip(skill_frame.Term,skill_frame.NumPostings) 
    
    tmp = WordCloud(width=800, height=330,ranks_only=True,background_color='white',margin = 5).generate_from_frequencies(words)
    default_colors = tmp.to_array()
    tmp.to_file("cloudSkills.png")
    
    plt.imshow(default_colors)
    plt.axis("off")
    plt.show()