# app/routes.py
from flask import render_template, redirect, url_for, flash, request
from datetime import datetime, timedelta
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db, login_manager  # Import only extensions, not app instance
from forms import LoginForm, ArticleSubmissionForm, AdminRegisterForm, ContactForm, CommentForm
from models import User, Article, Comment, Message, Visit
from werkzeug.utils import secure_filename
import os
from sqlalchemy import or_

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app):
    """Register all routes with the Flask app"""
    
    # Configure upload folder
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        page = request.args.get('page', 1, type=int)
        category = request.args.get('category')
        search_query = request.args.get('search', '', type=str)
        per_page = 5

        trending_articles = Article.query.order_by(Article.likes.desc()).limit(3).all()

        # Start with base query
        query = Article.query.filter(Article.status == 'approved')

        # Apply category filter
        if category:
            query = query.filter(Article.category == category)

        # Apply search filter (searching in title and content)
        if search_query:
            query = query.filter(
                or_(
                    Article.title.ilike(f'%{search_query}%'),
                    Article.content.ilike(f'%{search_query}%')
                )
            )

        # Finalize with ordering and pagination
        articles = query.order_by(Article.likes.desc(), Article.date_posted.desc())\
                        .paginate(page=page, per_page=per_page)

        categories = db.session.query(Article.category).distinct().all()

        return render_template('home.html', articles=articles, categories=categories, 
                               selected_category=category, search_query=search_query, trending_articles=trending_articles)

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

        # Increment views
        article.views = article.views + 1 if article.views else 1
        db.session.commit()

        # Log visit
        visit = Visit(article_id=article.id)
        db.session.add(visit)
        db.session.commit()

        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(
                content=form.content.data,
                user_id=current_user.id,
                article_id=article.id,
                parent_id=form.parent_id.data or None
            )
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('article_detail', article_id=article.id))

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

        form.category.choices = [(cat, cat) for cat in [...]]  # your categories list

        if form.validate_on_submit():
            # ✅ Correctly get the uploaded image and document from the form
            cover_image_file = form.cover_image.data
            document_file = form.document.data

            # Save cover image if present
            cover_image_filename = None
            if cover_image_file and cover_image_file.filename:
                cover_image_filename = secure_filename(cover_image_file.filename)
                cover_image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cover_image_filename))

            # Save document if present
            document_filename = None
            if document_file and document_file.filename:
                document_filename = secure_filename(document_file.filename)
                document_file.save(os.path.join(app.config['UPLOAD_FOLDER'], document_filename))

            # Create article record
            article = Article(
                author=form.author.data,
                email=form.email.data,
                title=form.title.data,
                content=form.content.data,
                category=form.category.data,
                cover_image=cover_image_filename,
                document_filename=document_filename
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
        total_articles = Article.query.count()
        total_visits = Visit.query.count()

        now = datetime.utcnow()

        daily_visits = Visit.query.filter(Visit.timestamp >= now - timedelta(days=1)).count()
        weekly_visits = Visit.query.filter(Visit.timestamp >= now - timedelta(weeks=1)).count()
        monthly_visits = Visit.query.filter(Visit.timestamp >= now - timedelta(days=30)).count()
        yearly_visits = Visit.query.filter(Visit.timestamp >= now - timedelta(days=365)).count()

        readers_per_article = db.session.query(
            Article.title, db.func.count(Visit.id)
        ).join(Visit, Article.id == Visit.article_id).group_by(Article.id).all()

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
            approved_articles=approved,
            total_articles=total_articles,
            total_visits=total_visits,
            daily_visits=daily_visits,
            weekly_visits=weekly_visits,
            monthly_visits=monthly_visits,
            yearly_visits=yearly_visits,
            readers_per_article=readers_per_article
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
            new_message = Message(
                name=form.name.data,
                email=form.email.data,
                message=form.message.data
            )
            db.session.add(new_message)
            db.session.commit()
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('contact'))
        return render_template('contact.html', form=form)

    @app.route('/messages')
    @login_required
    def view_messages():
        messages = Message.query.order_by(Message.date_sent.desc()).all()
        return render_template('messages.html', messages=messages)

    @app.route('/article/<int:article_id>/comment', methods=['POST'])
    def comment(article_id):
        name = request.form['name']
        content = request.form['comment']
        comment = Comment(name=name, content=content, article_id=article_id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('read_more', article_id=article_id))