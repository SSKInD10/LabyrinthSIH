from app import app
from flask import render_template,flash,redirect,url_for
from app.forms import LoginForm
import pandas as pd
from bokeh.embed import json_item,components
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.palettes import Category20c
from bokeh.transform import cumsum
from math import pi
import json,random
from flask_table import Table, Col

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from jinja2 import Template
# Use a service account
cred = credentials.Certificate('C:/Users/surya_eyj1nxg/Desktop/HTML+CSS Tutorial/labyrinth-beta-firebase-adminsdk-11dpd-9848444922.json')
firebase_admin.initialize_app(cred)


class Post(object):
    def __init__(self,name='',domain='',scores={},picture='',timestamp='00-00-0000 00:00:00'):
        self.name = name
        self.domain = domain
        self.scores = scores
        self.picture = picture
        self.timestamp = timestamp
    @staticmethod
    def from_dict(src):
        post = Post(src[u'name'],src[u'domain'],src[u'scores'],src[u'picture'])
        #if src[u'timestamp']:
        #    post[u'timestamp']=src[u'timestamp']
        return post
    def to_dict(self):
        dest = {u'name':self.name,
                u'domain':self.domain,
                u'scores':self.scores,
                u'picture':self.picture}
        #if self.timestamp:
        #    dest[u'timestamp']=self.timestamp
        return dest
    def __repr__(self):
        return(u'Post(name={}, domain={}, scores={}, picture={},timestamp={})'.format(self.name, self.domain, self.scores, self.picture,self.timestamp))

columns = [
  {"field": 'post_id', "title": "Post ID","sortable": False},
  {"field": u'name',"title": "Username","sortable": True},
  {"field": u'domain',"title": "Domain","sortable": True},
  {"field": u'timestamp',"title": "Time","sortable": True}
]

page = Template('''<!DOCTYPE html>
<html lang="en" dir="ltr">
  <head>
    <meta charset="utf-8">
    <title>{{title}}-Labyrinth</title>
    {{resources}}
    {{script}}
  </head>
  <body>
    <div>Labyrinth :
    <a href="/home">Home</a>
    <a href="/login">Login</a>
    <a href="/analyse">Data Analysis</a>
    </div>
    <hr>
    <h1>Post Details</h1>
    {{div}}
  </body>
</html>''')


# Declare your table
class ItemTable(Table):
    post_id = Col('Post ID')
    name = Col('Name')
    domain = Col('Domain')
    timestamp = Col('Timestamp')

def make_plot(x):
    data = pd.Series(x).reset_index(name='value').rename(columns={'index':'parameter'})
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    data['color'] = Category20c[len(x)]

    p = figure(plot_height=350, title="Pie Chart",#, toolbar_location=None,tools="hover",
    tooltips="@parameter: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='parameter', source=data)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None

    return p


@app.route('/')
@app.route('/home')
def home():
    user1 = {'username':'Admin'}
    return render_template('home.html',title='Index',user=user1)

@app.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign-In', form=form)

@app.route('/analyse')
def analyse():
    db = firestore.client()
    doc_ref = db.collection(u'flagged_posts')
    res = doc_ref.stream()
    data = []
    for doc in res:
        post = doc.to_dict()
        data.append({'post_id':doc.id,'name':post[u'name'],'domain':post[u'domain'],'timestamp':''})
    table = ItemTable(data)
    return render_template('analyse.html',bin=table)

@app.route('/post/<post_id>')
def post(post_id):
    db = firestore.client()
    doc_ref = db.collection(u'flagged_posts').document(str(post_id))
    try:
        doc = doc_ref.get()
    except google.cloud.exceptions.NotFound:
        return "Not Found"
    post = doc.to_dict()
    scores = post[u'scores']
    p = make_plot(scores)
    script1,div1 = components(p)
    return render_template('post.html',resources=CDN.render(),script=script1,div=div1,uname=post[u'name'],dom=post[u'domain'])
    #return page.render(title="Post Details",resources=CDN.render(),script=script1,div=div1)

@app.route('/profile/<uname>')
def profile(uname):
    db = firestore.client()
    query = db.collection(u'flagged_posts').where(u'name','==','uname')
    ctr = 0
    ctrd = {u'FaceBook':0,
            u'Twitter':0,
            u'Reddit':0,
            u'Hackernews':0,
            u'Instagram':0}
    avg_val = {
        u'SexualContent':0,
        u'Hate':0,
        u'Insult':0,
        u'Obscene':0,
        u'SevereToxic':0,
        u'Toxic':0,
        u'Threat':0,
        u'Sarcasm':0
    }
    for doc in query.stream():
        ctr -=- 1
        post = doc.to_dict()
        ctrd[post[u'domain']] -=- 1
        for k,v in post[u'scores']:
            avg_val[k]+=v
    p1 = make_plot(avg_val)
    p2 = make_plot(ctrd)
    script1,div1 = components(p1)
    script2,div2 = components(p2)
    return render_template('userprofile.html',resources=CDN.render(),scriptA=script1,divA=div1,scriptB=script2,divB=div2,username = uname)
