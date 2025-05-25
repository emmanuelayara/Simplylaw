# app/routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import app, db, login_manager
from forms import LoginForm, ArticleSubmissionForm, AdminRegisterForm, ContactForm, CommentForm
from models import Message
from models import User, Article, Comment
from werkzeug.security import generate_password_hash
from flask import request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
import os
from flask import render_template

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    per_page = 5  # number of articles per page

    if category:
        articles = Article.query.filter_by(category=category, status='approved')\
                                .order_by(Article.likes.desc(), Article.date_posted.desc())\
                                .paginate(page=page, per_page=per_page)
    else:
        articles = Article.query.filter_by(status='approved')\
                                .order_by(Article.likes.desc(), Article.id.desc())\
                                .paginate(page=page, per_page=per_page)

    categories = db.session.query(Article.category).distinct().all()

    return render_template('home.html', articles=articles, categories=categories, selected_category=category)




@app.route('/admin/approve/<int:article_id>')
def approve_article(article_id):
    article = Article.query.get_or_404(article_id)
    article.status = 'approved'
    db.session.commit()
    flash('Article approved successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/disapprove/<int:article_id>')
def disapprove_article(article_id):
    article = Article.query.get_or_404(article_id)
    article.status = 'disapproved'
    db.session.commit()
    flash('Article disapproved.', 'warning')
    return redirect(url_for('admin_dashboard'))


@app.route('/article/<int:article_id>')
def view_article(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('view_article.html', article=article)

@app.route('/read/<int:article_id>')
def read_more(article_id):
    article = Article.query.get_or_404(article_id)
    comments = Comment.query.filter_by(article_id=article_id).order_by(Comment.date_posted.desc()).all()
    return render_template('read_more.html', article=article, comments=comments)

@app.route('/like/<int:article_id>', methods=['POST'])
def like_article(article_id):
    article = Article.query.get_or_404(article_id)

    if article.likes is None:
        article.likes = 0  # safety fallback
        
    # Optional: Prevent multiple likes using IP address or user ID
    article.likes += 1
    db.session.commit()
    flash('You liked the article.', 'success')
    return redirect(request.referrer or url_for('read_more', article_id=article_id))


@app.route('/submit', methods=['GET', 'POST'])
def submit_article():
    form = ArticleSubmissionForm()
    
    # Set category choices dynamically (or statically)
    form.category.choices = [
        ("Criminal Law"), ("Family Law"), ("Constitutional Law"), 
        ("Tech Law"), ("Property Law"), ("Administrative Law"), 
        ("International Law"), ("Contract Law"), ("Tort Law"),
        ("Succession Law"), ("Corporate Law"), ("Commercial Law"), 
        ("Banking and Finance Law"), ("Securities Law"), ("Civil Litigation"), 
        ("Criminal Litigation"), ("Alternative Dispute Resolution"), ("Environmental Law"), 
        ("Energy Law"), ("Intellectual Property Law"), ("Copyright Law"), 
        ("Patent Law"), ("Trademark Law"), ("Trade Secrets Law"), 
        ("Labour and Employment Law"), ("Human Rights Law"), ("Health and Medical Law"), 
        ("Real Estate Law"), ("Transportation Law"), ("Cyber Law"), 
        ("Data Protection and Privacy Law"), ("Space Law"), ("Sports and Entertainment Law"), 
        ("Media and Communications Law"), ("Education Law"), ("Agricultural Law"), 
        ("Animal Law"), ("Maritime and Admiralty Law"), ("Immigration Law"), 
        ("Tax Law"), ("Military Law"), ("Bankruptcy Law"), 
        ("Consumer Protection Law"), ("Public Interest Law"), ("Customary and Indigenous Law")
    ]

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
            category=form.category.data,
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

    pending_page = request.args.get('pending_page', 1, type=int)
    approved_page = request.args.get('approved_page', 1, type=int)
    per_page = 3

    pending = Article.query.filter_by(status='pending')\
                .order_by(Article.date_posted.desc())\
                .paginate(page=pending_page, per_page=per_page)

    approved = Article.query.filter_by(status='approved')\
                .order_by(Article.date_posted.desc())\
                .paginate(page=approved_page, per_page=per_page)

    return render_template(
        'admin_dashboard.html',
        articles=pending,
        approved_articles=approved
    )


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


@app.route('/article/<int:article_id>/comment', methods=['POST'])
def comment(article_id):
    name = request.form['name']
    content = request.form['comment']
    comment = Comment(name=name, content=content, article_id=article_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('read_more', article_id=article_id))
