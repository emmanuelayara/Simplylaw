# app/routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from main import app, db, login_manager
from forms import LoginForm, ArticleSubmissionForm, AdminRegisterForm, ContactForm, CommentForm
from models import Message
from models import User, Article
from werkzeug.security import generate_password_hash
from flask import request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
import os
from flask import render_template
from main import app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    articles = Article.query.filter_by(approved=True).order_by(Article.id.desc()).all()
    return render_template('home.html', articles=articles)

@app.route('/admin/approve/<int:article_id>')
@login_required
def approve_article(article_id):
    article = Article.query.get_or_404(article_id)
    article.is_approved = True
    db.session.commit()
    flash('Article approved.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/disapprove/<int:article_id>')
def disapprove_article(article_id):
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    flash('Article disapproved and deleted.', 'danger')
    return redirect(url_for('admin_dashboard'))



@app.route('/article/<int:article_id>')
def view_article(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('view_article.html', article=article)



@app.route('/submit', methods=['GET', 'POST'])
def submit_article():
    form = ArticleSubmissionForm()
    
    if form.validate_on_submit():
        # Handle image upload
        image = request.files.get('image')
        image_filename = None
        if image and image.filename:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Handle document upload
        document = request.files.get('document')
        document_filename = None
        if document and document.filename:
            document_filename = secure_filename(document.filename)
            document.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))

        # Create article object
        article = Article(
            author=form.author.data,
            email=form.email.data,
            title=form.title.data,
            content=form.content.data,
            image_filename=image_filename,             # Optional: ensure this exists in your model
            document_filename=document_filename        # Optional: ensure this exists in your model
        )
        
        db.session.add(article)
        db.session.commit()
        flash('Article submitted successfully and is awaiting approval.', 'success')
        return redirect(url_for('home'))

    return render_template('submit_article.html', form=form)


@app.route('/admin/register', methods=['GET', 'POST'])
def register_admin():
    form = AdminRegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists.", "danger")
            return redirect(url_for('register_admin'))
        
        hashed_password = generate_password_hash(form.password.data)
        new_admin = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            is_admin=True
        )
        db.session.add(new_admin)
        db.session.commit()
        flash("Admin registered successfully!", "success")
        return redirect(url_for('admin_login'))
    return render_template('admin_register.html', form=form)



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data) and user.is_admin:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials or not an admin.', 'danger')
    return render_template('admin_login.html', form=form)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('home'))
    pending = Article.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', articles=pending)



@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data
        )
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)
