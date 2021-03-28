from flask import Flask, render_template, request, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import os
import re

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite3')

db=SQLAlchemy(app)

def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)

class Leader(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(140))
    number = db.Column(db.Integer)
    event = db.Column(db.String(140))



class Event(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    body = db.Column(db.Text)

    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug= slugify(self.title)
        else:
            self.slug = str(int(time()))
    
    def __repr__(self):
        return f'<Post id:{self.id}, title:{self.title}>'

@app.route('/')
def index():
    events = Event.query.order_by(Event.id.desc())
    page =request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page=1

    pages = events.paginate(page = page, per_page=5)
    return render_template('index.html',events=events , pages = pages )

@app.route('/<slug>')
def show(slug):
    p = Event.query.filter(Event.slug == slug).first()
    leaders = Leader.query.order_by(Leader.number.desc()).filter(Leader.event==p.title)
    page =request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page=1

    pages = leaders.paginate(page = page, per_page=5)
    return render_template('show.html',leaders=leaders , pages = pages , slug = slug )

@app.route('/<slug>/new' , methods=['POST','GET'])
def new(slug):
    p = Event.query.filter(Event.slug == slug).first()
    if request.method == 'POST':
        name = request.form['name']
        number = int(request.form['number'])
        leader = Leader( name = name , number = number , event = p.title )
        db.session.add(leader)
        db.session.commit()  
        return redirect(url_for('show' , slug = p.slug))
    return render_template('new.html', slug = p.slug)

@app.route('/create' , methods=['POST','GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        event = Event( title = title , body = body)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('show',slug= event.slug))
    return render_template('create.html')

if __name__ == '__main__':
    app.run(debug=True)
    manager.run()