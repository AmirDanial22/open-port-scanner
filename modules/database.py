from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), nullable=False)
    scan_date = db.Column(db.DateTime, nullable=False, default=db.func.now())
    results = db.Column(db.JSON, nullable=False)  # Menyimpan hasil scan dalam format JSON