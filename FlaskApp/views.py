from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from FlaskApp.forms import RegisterForm,ArticleForm
from FlaskApp import app,db
import FlaskApp.models as models
from passlib.hash import sha256_crypt
from functools import wraps

imageSourceUrl = 'https://'+ app.config['BLOB_ACCOUNT']  + '.blob.core.windows.net/' + app.config['BLOB_CONTAINER']  + '/'

# Index
@app.route('/')
def index():
    return render_template('home.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Articles
@app.route('/articles')
def articles():
    articles= models.Article.query.all()
    if len(articles) > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
   


#Single Article
@app.route('/article/<string:id>/')
def article(id):
    article = models.Article.query. get_or_404(int(id))

    return render_template('article.html', article=article, imageSource=imageSourceUrl)





# article Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        user = models.User(name=name,email=email,username=username,password=password)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# article login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password_candidate = request.form['password']
        user=models.User.query.filter_by(username=username).first()
       

        if user!=None:
            
            if sha256_crypt.verify(password_candidate, user.password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            
        else:
            error = 'username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

# Check if article logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    articles= models.Article.query.all()

    if len(articles) > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
    # Close connection
    cur.close()



# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        article = models.Article(title=title,body=body,author=session['username'])
        article.save_changes(request.files['image_path'])
        db.session.add(article)
        db.session.commit()
        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form, imageSource=imageSourceUrl)


# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    article = models.Article.query.get(int(id))
    form = ArticleForm(formdata=request.form, obj=article)
    if request.method == 'POST' and form.validate():
        article.save_changes(request.files['image_path'])
        article.title = request.form['title']
        article.body = request.form['body']
        db.session.commit()
        

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form, imageSource=imageSourceUrl,article=article)

# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    article=models.Article.query.get_or_404(int(id))
    db.session.delete(article)
    db.session.commit()    
    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))

