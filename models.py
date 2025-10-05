from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    qualification = db.Column(db.String(200))
    address = db.Column(db.Text)

    def __repr__(self):
        return f"<User {self.id} {self.first_name} {self.last_name}>"
