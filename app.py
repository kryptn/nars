#!/usr/bin/python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
from flask import Flask, render_template
from jinja2 import evalcontextfilter, Markup
import urllib2

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

#ohgod this needs to be separated. or does it?
@app.route('/', defaults={'base':'right', 'page':'1'})
@app.route('/<base>/', defaults={'page':'1'})
@app.route('/<base>/category/<category>', defaults={'page':'1'})
@app.route('/<base>/tag/<tag>', defaults={'page':'1'})
@app.route('/<base>/page/<page>')
@app.route('/<base>/category/<category>/page/<page>')
@app.route('/<base>/tag/<tag>/page/<page>')
@app.route('/<base>/<title>/<id>')
def index(base, page=1, category=None, tag=None, title=None, id=None, debug=False):
	"""
	the actual websites has too many ads on it and my phone
	hates it so i made this.

	It grabs the 'storycontent' div from each page, which has the story.

	If it's there, it'll grab the 'wp-pagenavi' div so I don't have to
	rewrite the pagination for the entire website.  It doesn't show up on
	single posts

	This should generall work on any notalways[x] website and is easily
	expanded to new ones by modifying the 'bases' list
	
	"""

	bases = ['right','romantic','working','related']
	if base not in bases:
		base = 'right'

	url = 'http://notalways%s.com' % base

	if id:
		html = urllib2.urlopen('%s/%s/%s'               % (url,title,id)).read()
	elif category:
		html = urllib2.urlopen('%s/category/%s/page/%s' % (url,category,page)).read()
	elif tag:
		html = urllib2.urlopen('%s/tag/%s/page/%s'      % (url,tag,page)).read()
	else:
		html = urllib2.urlopen('%s/page/%s'             % (url, page)).read()

	if debug: return html

	for b in bases:
		html = html.replace('notalways%s.com' % b, 'welp.in/nar/%s' % b)
	#html = html.replace(u'href="/', 'href="/nar/%s/' % str(base)) need to fix (not sure why)

	soup, r = BeautifulSoup(html), list()
	stories = soup.findAll(attrs={'class':'post'})
	if id: stories = stories[:1]

	for s in stories:
		t = {'title': unicode(s.a),
			  'category': unicode(s.div),
			  'content': unicode(s.find('div','storycontent')) }
		if 'Announcements' not in t['category']:
			r.append(t)

	if id:
		pages = None
	else:
		pages = unicode(soup.find('div','wp-pagenavi'))


	return render_template('index.html', bases=bases, content=r, pages=pages)

if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)