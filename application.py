import os
import requests
import json
from flask import request

from flask import Flask, session,render_template,redirect,url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/",methods=["GET","POST"])
def home():
    username=session.get('username')
    session["book"]=[]
    message=""
    if request.method=="POST":
        search=request.form.get('search')
        search="%"+search+"%"
        result=db.execute("SELECT * FROM books WHERE isbn LIKE :r OR title LIKE :r OR author LIKE :r",{"r":search,"r":search,"r":search}).fetchall()
        for i in result:
            session['book'].append(i)
        if len(session["book"])==0:
            message="Not found, please try again"
        else:
            message="Search result"
    return render_template('index.html',username=username,message=message,result=session["book"])

@app.route("/isbn/<string:isbn>",methods=["GET","POST"])
def bookpage(isbn):
    username=session.get('username')
    session["review"]=[]
    message=""
    data=db.execute("SELECT * FROM books WHERE isbn=:i",{"i":isbn}).fetchone()
    
    res=requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"3FU5KyAbQ341jgF5QZxYQ","isbns":isbn})
    average_rating=res.json()["books"][0]["average_rating"]
    work_ratings_count=res.json()['books'][0]['work_ratings_count']
    
    checker=db.execute("SELECT review FROM reviews WHERE isbn=:i AND username=:u",{"i":isbn,"u":username}).fetchone()
    
    if request.method=="POST" and checker==None:
        rating=request.form.get('rating')
        review=request.form.get('review')
        if rating==None:
            message="Please pick a rating"
            return render_template('book.html',username=username,message=message,data=data,average_rating=average_rating,work_ratings_count=work_ratings_count,reviews=session["review"])
        else:
            db.execute("INSERT INTO reviews VALUES (:i,:u,:r,:ra)",{"i":isbn,"u":username,"r":review,"ra":rating})
            db.commit()
    if request.method=="POST" and checker!=None:
        message="You reviewed this book"
        
    reviews=db.execute("SELECT * FROM reviews WHERE isbn = :i",{"i":isbn}).fetchall()
    for i in reviews:
        session["review"].append(i)
    
    return render_template('book.html',username=username,message=message,data=data,average_rating=average_rating,work_ratings_count=work_ratings_count,reviews=session["review"])
 
@app.route("/api/<string:isbn>")
def API(isbn):
    data=db.execute("SELECT * FROM books WHERE isbn=:i",{"i":isbn}).fetchone()
    if data==None:
        return render_template('error.html')
    res=requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"3FU5KyAbQ341jgF5QZxYQ","isbns":isbn})
    average_rating=res.json()["books"][0]["average_rating"]
    work_ratings_count=res.json()['books'][0]['work_ratings_count']
    datajson={
        "title": data.title,
        "author": data.author,
        "year": data.year,
        "isbn": isbn,
        "review_count":work_ratings_count,
        "average_score": average_rating
    }
    api=json.dumps(datajson)
    return render_template('api.json',api=api)
    
@app.route("/registration",methods=["GET","POST"])
def registration():
    message="please fill in this form to create an account"
    render_template('register.html',message=message)
    if request.method=="POST":
        name=request.form.get('name')
        psw=request.form.get('psw')
        psw_repeat=request.form.get('psw_repeat')
        data=db.execute("SELECT username FROM users").fetchall()
        for i in range(len(data)):
            if data[i]["username"]==name:
                message="usename already exsist"
                return render_template('register.html',message=message)
        if psw!=psw_repeat:
            message="password is not same, please try again"
            return render_template('register.html',message=message)
        db.execute("INSERT INTO users(username,password) VALUES (:u,:p)",{"u":name,"p":psw})
        db.commit()
        message="You can access now"
    return render_template('register.html',message=message)

@app.route("/login",methods=["GET","POST"])
def login():
    message="please fill in this form to login"
    render_template('login.html',message=message)
    if request.method=="POST":
        name=request.form.get('name')
        psw=request.form.get('psw')
        data=db.execute("SELECT * FROM users WHERE username=:u",{"u":name}).fetchone()
        if data==None:
            message="user not found, please check your information or create an account"
            render_template('login.html',message=message)
        else:
            if data.username==name and data.password==psw:
                session["username"]=name
                return redirect(url_for("home"))
            else:
                message="invalid password, please try again"
                return render_template('login.html',message=message)
    return render_template('login.html',message=message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))
    