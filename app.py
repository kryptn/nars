#/usr/bin/python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup as bs
from collections import namedtuple
from flask import Flask, render_template, url_for
from jinja2 import evalcontextfilter, Markup
import urllib2

DOMAIN = "welp.in/nar"

app = Flask(__name__)

@app.template_filter()
@evalcontextfilter
def unescape(eval_ctx, s):
	s = s.replace('&lt;', '<')
	s = s.replace('&gt;', '>')
	s = s.replace('&amp;', '&')	
	if eval_ctx.autoescape: s = Markup(s)
	return s

@app.route('/', defaults={'page': '1'})
@app.route('/page/<page>')
@app.route('/<title>/<id>')
def index(page=1, title=None, id=None):
	if id:
		html = urllib2.urlopen("http://notalwaysright.com/"+title+"/"+id).read()
	else:
		html = urllib2.urlopen("http://notalwaysright.com/page/"+page).read()
	soup = bs(html)
	stories = soup.findAll(attrs={'class':'post'})
	r = []
	Content = namedtuple('Content', ['title','content'])
	for s in stories:
		title = unicode(s.a)
		content = unicode(s.find('div','storycontent'))
		title = title.replace("notalwaysright.com",DOMAIN)
		content = content.replace("notalwaysright.com",DOMAIN)
		r.append(Content(title, content))
	
	if id:
		pages = None
	else:
		pages = unicode(soup.find('div','wp-pagenavi'))
		pages = pages.replace("notalwaysright.com",DOMAIN)

	return render_template("index.html", content=r, pages=pages)


if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)