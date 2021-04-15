from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import requests
import csv


def get_skills(url):
    get_job_html = requests.get(url, timeout=5)
    if get_job_html.status_code == 200:
        get_job_html = get_job_html.text
    else:
        print('404 error')
    strainer = SoupStrainer('div', attrs={'class': 'tag-name'})
    job_soup = BeautifulSoup(get_job_html, 'lxml', parse_only=strainer)
    #job_soup = BeautifulSoup(get_job_html, 'lxml')
    skills_elements = job_soup.find_all('div', class_='tag-name')
    return [skill.text.strip() for skill in skills_elements]


def get_jobs(jobs, my_skills):
    jobs_listing = []
    for job in jobs:
        company_name = job.find('div', class_='small-txt').span.text.strip()
        job_title = job.h3.text.strip()
        job_url = job.h3.a['href']
        skills = get_skills(job_url)
        if 'Junior' in job_title:
            if any(item in my_skills for item in skills):
                jobs_listing.append([company_name, job_title, job_url, skills])
    return jobs_listing


def find_jobs(current_page, last_page, url, soup):
    jobs_list = []
    while current_page <= last_page:
        jobs = soup.find_all('div', class_='job-details-left')
        my_skills = ['Python', 'JavaScript']
        jobs_list += get_jobs(jobs, my_skills)
        current_page += 1
        html_text = requests.get(url + f'/page/{current_page}', timeout=5)
        if html_text.status_code == 200:
            html_text = html_text.text
            soup = BeautifulSoup(html_text, 'lxml')
        # else:
        #     print('404 error')

    with open('./posts/jobs.csv', 'w', encoding="utf-8") as f:
        csv_writer = csv.DictWriter(f, fieldnames=('CompanyName', 'JobTitle', 'JobUrl', 'Skills'), lineterminator='\n')
        csv_writer.writeheader()
        for job in jobs_list:
            csv_writer.writerow({
                'CompanyName': job[0],
                'JobTitle': job[1],
                'JobUrl': job[2],
                'Skills': ", ".join(job[3])
            })
    print(f'File saved')

startTime = datetime.now()

url = 'https://dev.bg/company/jobs/junior-intern/sofiya/'
html_text = requests.get(url, timeout=5)
if html_text.status_code == 200:
    html_text = html_text.text
    soup = BeautifulSoup(html_text, 'lxml')
    current_page = 1
    last_page = int([page.text.replace('\n', '').strip()
                     for page in soup
                    .find('div', class_='page-number-holder')
                    .find_all('div', class_='page-nav')][-1])
    find_jobs(current_page, last_page, url, soup)
else:
    print('404 error')

print(datetime.now() - startTime)
