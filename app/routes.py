from flask import render_template, redirect, url_for, flash, request, session
from flask import current_app as app
from .models import Post, Comment, Message, User
from .forms import CommentForm, ContactForm, LoginForm, PostForm
from .import db
from functools import wraps
from app.models import User


def register_routes(app):

    @app.route('/')
    def home():
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        return render_template('home.html', posts=posts)

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "admin_user" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated_function


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

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                session["admin_user"] = user.username
                flash("Logged in successfully!", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Invalid username or password", "danger")
        return render_template("login.html", form=form)

    @app.route("/admin")
    @login_required
    def admin_dashboard():
        posts = Post.query.order_by(Post.date_posted.desc()).all()
        return render_template("dashboard.html", posts=posts)

    @app.route("/admin/create", methods=["GET", "POST"])
    @login_required
    def create_post():
        form = PostForm()
        if form.validate_on_submit():
            post = Post(title=form.title.data, content=form.content.data)
            db.session.add(post)
            db.session.commit()
            flash("Post created!", "success")
            return redirect(url_for("admin_dashboard"))
        return render_template("admin/create_post.html", form=form)

    @app.route("/admin/edit/<int:post_id>", methods=["GET", "POST"])
    @login_required
    def edit_post(post_id):
        post = Post.query.get_or_404(post_id)
        form = PostForm(obj=post)
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash("Post updated!", "success")
            return redirect(url_for("admin_dashboard"))
        return render_template("admin/edit_post.html", form=form, post=post)

    @app.route("/admin/delete/<int:post_id>")
    @login_required
    def delete_post(post_id):
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted!", "info")
        return redirect(url_for("admin_dashboard"))

    @app.route("/logout")
    def logout():
        session.pop("admin_user", None)
        flash("Logged out successfully.", "info")
        return redirect(url_for("login"))

    @app.route('/post/<int:post_id>', methods=['GET', 'POST'])
    def post(post_id):
        post = Post.query.get_or_404(post_id)
        form = CommentForm()
        if form.validate_on_submit():
            comment = Comment(
                name=form.name.data,
                email=form.email.data,
                content=form.content.data,
                post_id=post.id
            )
            db.session.add(comment)
            db.session.commit()
            flash('Your comment has been posted!', 'success')
            return redirect(url_for('post', post_id=post.id))
        comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
        return render_template('post.html', post=post, comments=comments, form=form)
