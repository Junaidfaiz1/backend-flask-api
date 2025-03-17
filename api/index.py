from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
from api.scrapjob import ScrapJob, ScrapCategories 
from api.routes.job_routes import job_bp
load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)
app.register_blueprint(job_bp)

@app.route('/')
def home():
    return jsonify({"status": "success", "message": "API is running"}), 200

@app.route('/api/cron/scrape-jobs')
def trigger_job_scrape():
    try:
        ScrapJob()
        return jsonify({"status": "success", "message": "Jobs scraping completed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/cron/scrape-categories')
def trigger_categories_scrape():
    try:
        ScrapCategories()
        return jsonify({"status": "success", "message": "Categories scraping completed"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# For local development only
if __name__ == "__main__":
    from apscheduler.schedulers.background import BackgroundScheduler
    
    with app.app_context():
        db.create_all()
    
    scheduler = BackgroundScheduler()
    scheduler.add_job(trigger_job_scrape, "interval", minutes=45)
    scheduler.start()

    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        scheduler.shutdown()