import time
from bs4 import BeautifulSoup
import requests
import logging
from api.models.jobs import db, Job
from api.models.jobs import Keyword
from api.models.jobs import Category, Tags


logging.basicConfig(filename= "scraper.log", level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ScrapJob():
    logging.info("Executing ScrapJob...")
    page = 1
    url = f"https://www.actuarylist.com/?page="

    while True:
        response = requests.get(f"{url}{page}")

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "lxml")
        jobs = soup.find_all("article")

        if not jobs:
            break

        for job in jobs:
            try:
                company_name = job.find("p", class_="Job_job-card__company__7T9qY")
                company_name = company_name.text.strip() if company_name else "N/A"

                job_title = job.find("p", class_="Job_job-card__position__ic1rc")
                job_title = job_title.text.strip() if job_title else "N/A"

                job_posted = job.find("p", class_="Job_job-card__posted-on__NCZaJ")
                job_posted = job_posted.text.strip() if job_posted else "N/A"

                post_url = job.find("a", class_="Job_job-page-link__a5I5g")
                post_url = "https://www.actuarylist.com/" + post_url.get("href") if post_url else "N/A"

                job_country = job.find("a", class_="Job_job-card__country__GRVhK")
                job_country = job_country.text.strip() if job_country else "Location Not Found"

                job_salary = job.find("p", class_="Job_job-card__salary__QZswp")
                job_salary = job_salary.text.strip().replace("💰", "") if job_salary else "Salary Not Given"
               
                keywords = []
                job_tags_section = job.find("div", class_="Job_job-card__tags__zfriA")
                if job_tags_section:
                    keyword_elements = job_tags_section.find_all("a", class_="Job_job-card__location__bq7jX")
                    keywords = [keyword.text.strip() for keyword in keyword_elements]
                
                
                if not db.session.query(Job).filter_by(title=job_title, company_name=company_name).first():
                    new_job = Job(
                    title=job_title,
                    company_name=company_name,
                    country=job_country,
                    salary=job_salary,
                    post_url=post_url,
                    posted_on=job_posted,
                    )
                    db.session.add(new_job)
                    db.session.commit()
                    
                    for keyword in keywords[0:]:
                        existing_keyword = db.session.query(Keyword).filter_by(name=keyword).first()
                        if not existing_keyword:
                                new_keyword = Keyword(name=keyword)
                                db.session.add(new_keyword)
                                db.session.commit()
                                new_job.keywords.append(new_keyword)  
                        else:
                                new_job.keywords.append(existing_keyword)
                    db.session.commit()

                else:
                    continue

            except Exception as e:
                logging.error(f"Error processing job: {e}")

       
        page += 1
        time.sleep(2)

        if page == 10: 
            logging.info("Page {page} is done")
            break


def ScrapCategories():
    logging.info("Executing ScrapCategories...")
    url = "https://www.actuarylist.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")
   

    form = soup.find_all("aside", class_="hidden lg:block")
    for sections in form:
        section = sections.find_all("fieldset")
        for field in section:
            if field.find("legend"):
                category_name = field.find("legend").text.strip()
                existing_category = db.session.query(Category).filter_by(name=category_name).first()
                if not existing_category:
                    new_category = Category(name=category_name)
                    db.session.add(new_category)
                    db.session.commit()
                else:
                    continue

                field_name = field.find("div", class_="space-y-3 pt-4")

                if field_name:
                    checkboxes = field_name.find_all("label")  
                    for checkbox in checkboxes:
                        label_text = checkbox.get_text(separator=" ", strip=True)
                        
                        existingtag = db.session.query(Tags).filter_by(word=label_text).first()
                        if not existingtag:
                            new_tag = Tags(word=label_text)
                            new_category.tags.append(new_tag)
                            db.session.add(new_tag)
                            db.session.commit()
                        else:
                            new_category.tags.append(existingtag)
                    db.session.commit()
                            

if __name__ == "__main__":
    ScrapCategories()  
    ScrapJob()  
    logging.info("Job scraping end...")