#!/usr/bin/python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup as bs
from flask import Flask, render_template, url_for, redirect
from jinja2 import evalcontextfilter, Markup
import urllib2

DOMAIN = "welp.in/nar"

app = Flask(__name__)

@app.template_filter()
@evalcontextfilter
def unescape(eval_ctx, s):
	""" adds a jinja filter to unescape html entities """
	s = s.replace('&lt;', '<')
	s = s.replace('&gt;', '>')
	s = s.replace('&amp;', '&')	
	if eval_ctx.autoescape: s = Markup(s)
	return s

@app.route('/', defaults={'base':'right', 'page':'1'})
@app.route('/<base>/', defaults={'page':'1'})
@app.route('/<base>/page/<page>')
@app.route('/<base>/<title>/<id>')
def index(base, page=1, title=None, id=None):
	"""
	the actual websites has too many ads on it and my phone
	hates it so i made this.

	It grabs the 'storycontent' div from each page, which has the story.

	If it's there, it'll grab the 'wp-pagenavi' div so I don't have to
	rewrite the pagination for the entire website.  It doesn't show up on
	single posts

	Should be easy to change to almost any wordpress blog.
	May be extendable with Flask blueprints?
	
	"""

	bases = ['right','romantic','working','related']
	if base in bases:
		pass
	else:
		base = 'right'

	url = 'http://notalways%s.com/' % base

	if id:
		html = urllib2.urlopen(url+title+'/'+id).read()
	else:
		html = urllib2.urlopen(url+"page/"+page).read()

	for b in bases:
		html = html.replace('notalways%s.com'%b,'welp.in/nar/'+b)

	soup, r = bs(html), list()
	stories = soup.findAll(attrs={'class':'post'})
	if id: stories = stories[:1]

	for s in stories:
		t = {'title': unicode(s.a),
			  'category': unicode(s.div.text),
			  'content': unicode(s.find('div','storycontent')) }
		r.append(t)

	if id:
		pages = None
	else:
		pages = unicode(soup.find('div','wp-pagenavi'))

	return render_template('index.html', content=r, pages=pages)


if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)