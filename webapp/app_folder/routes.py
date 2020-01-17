from app_folder.models import User, Post
from app_folder import app, db, bcrypt, lang_processor
from flask import Flask, render_template, request, flash, redirect, url_for
from app_folder.forms import RegistrationForm, LoginForm, JournalForm
from flask_login import login_user, current_user, logout_user

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('secondpage.html')

@app.route('/journalentry', methods=['Get', 'POST'])
def journalentry():
    if not current_user.is_authenticated:
        return redirect(url_for('register'))
    form = JournalForm()
    if form.validate_on_submit():
        text = form.text.data
        sentiment = lang_processor.sample_analyze_sentiment(text).document_sentiment.score
        post = Post(sentiment=sentiment, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('analytics'))
    return render_template('journal-entry.html', title='Entry', form=form)

@app.route('/analytics')
def analytics():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    myposts = Post.query.filter_by(user_id=current_user.id).all()
    total = 0
    for post in myposts:
        total+=post.sentiment
    avg = total/len(myposts)

    message = ''
    if avg < 0:
        message = '''Your posts show that you might not be going through the best of time.'
                    Maybe you should seek help and talk about it with a loved one or medical professional'''
    elif avg<0.5:
        message = '''Your posts show that you are having some decent times! Here's to many more happy days'''
    else:
        message = '''Your posts show that you are having some AMAZING days! Enjoy them to the fullest!
                    This is what life is about!'''
    return render_template('analytics.html',avg=avg, message=message)


@app.route('/register', methods=['Get','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    form1 = LoginForm()

    if form.submit.data and form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f'Account created for {form.username.data} successfully! You can now login')
        return redirect(url_for('journalentry'))
    elif form1.validate_on_submit():
        user = User.query.filter_by(email=form1.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form1.password.data):
            login_user(user, remember=form1.remember.data)
            return redirect(url_for('journalentry'))
    return render_template('register.html', title='Register', form=form, form1=form1)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
