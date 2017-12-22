# Resume matcher- find a job on Glassdoor

For this project, I scrape Glassdoor.ca, a California-based company that provides a database of job postings along with company and salary reviews, and interview tips. Developed in Python and deployed as a web application using R, this program allows a user to upload and match their resume to available job postings on Glassdoor. I use cosine similarity as my distance metric.

Brief description of the code:
helper.py: Helper methods for scraping and resume text analysis
scrapeGlassdoor.py: Scrape Glassdoor to obtain the data
app.R: The R-Shiny app.
