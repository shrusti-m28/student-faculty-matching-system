from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///studyconnect.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---------------- MODELS ----------------

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(20))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    skills = db.Column(db.String(300))
    interest = db.Column(db.String(200))
    projects = db.Column(db.String(300))

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fid = db.Column(db.String(20))
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    skills = db.Column(db.String(300))
    interest = db.Column(db.String(200))
    projects = db.Column(db.String(300))

# ---------------- HOME ----------------

@app.route("/")
def home():
    return "StudyConnect Running Successfully"

# ---------------- DB ----------------

@app.route("/create_db")
def create_db():
    db.create_all()
    return jsonify({"msg": "Database Created"})

# ---------------- SEED ----------------

@app.route("/seed")
def seed():

    db.session.query(Student).delete()
    db.session.query(Faculty).delete()
    db.session.commit()

    students = [
        Student(sid="STU001", name="Arjun", email="arjun@gmail.com", password="123", contact="9876543210", skills="Python, AI", interest="AI", projects="Chatbot"),
        Student(sid="STU002", name="Priya", email="priya@gmail.com", password="123", contact="9123456780", skills="HTML, CSS", interest="Web", projects="Website"),
        Student(sid="STU003", name="Rahul", email="rahul@gmail.com", password="123", contact="9988776655", skills="Python, Data", interest="Data", projects="Dashboard"),
        Student(sid="STU004", name="Sneha", email="sneha@gmail.com", password="123", contact="9090909090", skills="C++, DSA", interest="CP", projects="Coding"),
        Student(sid="STU005", name="Vikram", email="vikram@gmail.com", password="123", contact="9876501234", skills="Flutter", interest="App", projects="Mobile App"),
    ]

    faculties = [
        Faculty(fid="FAC001", name="Dr Rao", email="rao@pu.edu", password="123", contact="8001122233", skills="AI, ML", interest="AI", projects="AI System"),
        Faculty(fid="FAC002", name="Dr Sharma", email="sharma@pu.edu", password="123", contact="8002233344", skills="Web, React", interest="Web", projects="Portal"),
        Faculty(fid="FAC003", name="Dr Mehta", email="mehta@pu.edu", password="123", contact="8003344455", skills="Data, Python", interest="Data", projects="Analytics"),
        Faculty(fid="FAC004", name="Dr Kumar", email="kumar@pu.edu", password="123", contact="8004455566", skills="AI", interest="AI", projects="Deep Learning"),
        Faculty(fid="FAC005", name="Dr Iyer", email="iyer@pu.edu", password="123", contact="8005566677", skills="Python", interest="Data", projects="ML Model"),
    ]

    db.session.add_all(students + faculties)
    db.session.commit()

    return jsonify({"msg": "Seed Updated"})

# ---------------- REGISTER ----------------

@app.route("/register", methods=["POST"])
def register():

    data = request.json

    if data["role"] == "student":
        user = Student(
            sid="STU"+data["email"][:3],
            name=data["name"],
            email=data["email"],
            password=data["password"],
            contact=data["contact"],
            skills=data["skills"],
            interest=data["interest"],
            projects=data["projects"]
        )
    else:
        user = Faculty(
            fid="FAC"+data["email"][:3],
            name=data["name"],
            email=data["email"],
            password=data["password"],
            contact=data["contact"],
            skills=data["skills"],
            interest=data["interest"],
            projects=data["projects"]
        )

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Registered Successfully"})

# ---------------- LOGIN ----------------

@app.route("/login", methods=["POST"])
def login():

    data = request.json

    if data["role"] == "student":
        user = Student.query.filter_by(email=data["email"], password=data["password"]).first()
        role = "student"
        uid = user.sid if user else None
    else:
        user = Faculty.query.filter_by(email=data["email"], password=data["password"]).first()
        role = "faculty"
        uid = user.fid if user else None

    if not user:
        return jsonify({"error": "User Not Found"})

    return jsonify({
        "role": role,
        "id": uid,
        "name": user.name,
        "email": user.email,
        "contact": user.contact,
        "skills": user.skills,
        "interest": user.interest,
        "projects": user.projects
    })

# ---------------- MATCH ----------------

@app.route("/match", methods=["POST"])
def match():

    data = request.json
    role = data["role"]
    email = data["email"]

    results = []

    def get_suggestion(score, rtype):
        if rtype == "faculty":
            if score >= 80:
                return "Excellent match - Highly recommended mentor"
            elif score >= 60:
                return "Good match - Suitable guidance"
            elif score >= 40:
                return "Average match - Can collaborate"
            else:
                return "Low match - Explore others"
        else:
            if score >= 80:
                return "Top student - Strong project candidate"
            elif score >= 60:
                return "Good student - Can work under guidance"
            elif score >= 40:
                return "Average student - Needs improvement"
            else:
                return "Weak match"

    if role == "student":

        user = Student.query.filter_by(email=email).first()
        if not user:
            return jsonify([])

        faculties = Faculty.query.all()

        for f in faculties:

            score = 0

            if user.interest.lower() in f.interest.lower():
                score += 50

            for s in user.skills.split(","):
                if s.strip().lower() in f.skills.lower():
                    score += 40

            if score > 0:
                results.append({
                    "name": f.name,
                    "email": f.email,
                    "contact": f.contact,
                    "skills": f.skills,
                    "interest": f.interest,
                    "projects": f.projects,
                    "score": score,
                    "suggestion": get_suggestion(score, "faculty")
                })

    else:

        user = Faculty.query.filter_by(email=email).first()
        if not user:
            return jsonify([])

        students = Student.query.all()

        for s in students:

            score = 0

            if user.interest.lower() in s.interest.lower():
                score += 50

            for sk in s.skills.split(","):
                if sk.strip().lower() in user.skills.lower():
                    score += 40

            if score > 0:
                results.append({
                    "name": s.name,
                    "email": s.email,
                    "contact": s.contact,
                    "skills": s.skills,
                    "interest": s.interest,
                    "projects": s.projects,
                    "score": score,
                    "suggestion": get_suggestion(score, "student")
                })

    return jsonify(results if results else [{"name":"No Matches Found","score":0}])

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)