from app import app
from flask import render_template,flash,redirect,url_for
from app.forms import LoginForm
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
