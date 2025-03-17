from flask import Blueprint, request, jsonify
import sys
from pathlib import Path

# Add the api directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from models.jobs import Job
from models.jobs import db
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from models.jobs import Category, Keyword

job_bp = Blueprint("job_bp", __name__)


@job_bp.route("/createjob", methods=["POST"])
def create_job():
    data = request.json
    new_job = Job(
        title=data["title"],
        salary=data["salary"],
        company_name=data["company_name"],
        country=data["country"],
        post_url=data["post_url"],
        posted_on=data["posted_on"]
    )
    db.session.add(new_job)
    db.session.commit()
    return jsonify({"message": "Job created successfully"}), 201


@job_bp.route('/jobs', methods=['GET'])
def get_jobs():
    query = Job.query.options(joinedload(Job.keywords))

    # Get query parameters
    country = request.args.get('country')
    title = request.args.get('title')
    experience = request.args.get('experience')
    sectors = request.args.getlist('sector')  
    city = request.args.get('city')
    tags = request.args.get('tags')

    filters = [] 
    
    if country:
        filters.append(and_(Job.country.ilike(f"%{country}%")))

    if title:
        filters.append(Job.title.ilike(f"%{title}%"))

    if sectors:
        filters.append(Keyword.name.ilike(f"%{sectors}%"))

    if city:
        filters.append(Keyword.name.ilike(f"%{city}%"))
    if tags:
        filters.append(Keyword.name.ilike(f"%{tags}%"))
    if experience:
        filters.append(Keyword.name.ilike(f"%{experience}%"))

    if filters:
        query = query.join(Job.keywords).filter(and_(*filters))

    jobs = query.distinct().all()  
    return jsonify([
        {
            "job_id": job.job_id,
            "title": job.title,
            "company_name": job.company_name,
            "country": job.country,
            "salary": job.salary,
            "post_url": job.post_url,
            "posted_on": job.posted_on,
            "keywords": [kw.name for kw in job.keywords]
        }
        for job in jobs
    ])



   
   
"""@job_bp.route("/updatejob/<int:job_id>", methods=["PUT"])
def update_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"message": "Job not found"}), 404
    data = request.json

    job.title = data.get("title", job.title)
    job.salary = data.get("salary", job.salary)
    job.company_name = data.get("company_name", job.company_name)
    job.country = data.get("country", job.country)
    job.post_url = data.get("post_url", job.post_url)
    job.posted_on = data.get("posted_on", job.posted_on)
    db.session.commit()
    return jsonify({"message": "Job updated successfully"}), 200
"""

@job_bp.route("/deletejob/<int:job_id>", methods=["DELETE"])
def delete_job(job_id):
    job = Job.query.get(job_id)
    if not job:
        return jsonify({"message": "Job not found"}), 404
    
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted successfully"}), 200


@job_bp.route("/categories")
def categories():
    categories= Category.query.all()
    return jsonify([
        {
            "id": category.category_id,
            "name": category.name,
            "tags": [tag.word for tag in category.tags]
        }
        for category in categories
    ])


