from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


job_keywords = db.Table(
    "job_keywords",
    db.Column("job_id", db.Integer, db.ForeignKey("job.job_id"), primary_key=True),
    db.Column("keyword_id", db.Integer, db.ForeignKey("keyword.keyword_id"), primary_key=True),
)


category_tags = db.Table(
    "category_tags",
    db.Column("category_id", db.Integer, db.ForeignKey("category.category_id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.tag_id"), primary_key=True),
)


class Job(db.Model):
    __tablename__ = "job"
    job_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(255))
    salary = db.Column(db.String(255))
    post_url = db.Column(db.String(255), nullable=False)
    posted_on = db.Column(db.String(255), nullable=False)
    keywords = db.relationship("Keyword", secondary=job_keywords, back_populates="jobs")


    def __repr__(self):
        return f"<Job {self.title} at {self.company_name}>"


class Keyword(db.Model):
    __tablename__ = "keyword"
    keyword_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    jobs = db.relationship("Job", secondary=job_keywords, back_populates="keywords")
   
        

    def __repr__(self):
        return f"<Keyword {self.name}>"


class Tags(db.Model):
    __tablename__ = "tags"
    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String, nullable=False)
    categories = db.relationship("Category", secondary=category_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag {self.word}>"


class Category(db.Model):
    __tablename__ = "category"
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    tags = db.relationship("Tags", secondary=category_tags, back_populates="categories")


    def __repr__(self):
        return f"<Category {self.name}>"
