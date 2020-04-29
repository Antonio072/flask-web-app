#app/views.py

from flask import render_template

from data import *

data = Articles()



from app import app
	
@app.route('/')
def index():
	return render_template("index.html")

@app.route('/about')
def about():
	return render_template("about.html")

@app.route('/articles')
def articles():
	return render_template("articles.html", articles=data)


@app.route('/articles/<variable>', methods=['GET'])
def article(variable):
    		#do your code here
	article = data[int(variable)]	
  	return render_template("article.html",para1=article)
