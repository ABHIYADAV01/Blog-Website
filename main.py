from flask import Flask, render_template, request
from flask import session
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
import json
from flask_mail import Mail
from datetime import datetime

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)
app.secret_key = 'super-secret-key'   #this is set for the login page this has to be done in flask


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/chooseyourtech'
db = SQLAlchemy(app)


class Contacts(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    ph_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
   

@app.route("/")
def home():
    post = Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html',params=params, post=post)


@app.route("/about")
def about():
    return render_template('about.html',params=params)

@app.route("/dashboard",methods = ['GET','POST'])
def dashboard():

    if "user" in session and session['user']==params['admin_user']:
      posts= Posts.query.all()
      return render_template("dashboard.html",params=params,posts=posts)

    if request.method=="POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")
        if username==params['admin_user'] and userpass==params['admin_password']:
            #set the session variable
            session['user'] = username
            posts= Posts.query.all()
            return render_template("dashboard.html",params=params,posts=posts)
    else:    
        return render_template('login.html',params=params)
    


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)



@app.route("/edit/<string:sno>" , methods=['GET', 'POST'])
def edit(sno):
 if "user" in session and session['user']==params['admin_user']:
    if(request.method=='POST'):
        '''Add entry to the database'''
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        img_file = request.form.get('img_file')
        date= datetime.now()
        
        if sno=='0':
          post = Posts(title=title,slug=slug,content=content,img_file=img_file,date=date)
          db.session.add(post)
          db.session.commit()         
        else:
          post = Posts.query.filter_by(sno=sno).first()
          post.title = title
          post.slug = slug
          post.content = content
          post.img_file = img_file
          post.date = date
          db.session.commit()
          return redirect('/edit/'+sno)

 post = Posts.query.filter_by(sno=sno).first()
 return render_template('edit.html', params=params, post=post)


@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(name=name,email = email , ph_num = phone, msg = message, date= datetime.now())
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html',params=params)


app.run(debug=True)


