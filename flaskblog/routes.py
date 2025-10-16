from flask import render_template, url_for, redirect, flash, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.models import User, Post
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, NewPostForm
from flask_login import login_user, logout_user, current_user, login_required

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template("home.html", posts=posts)
    
    
@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("You have been logged in")
            return redirect(url_for("account"))
        else:
            flash("login unsuccessful. Please check email and password.")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", title="Account Page", form=form)


@app.route("/blog-post/<int:post_id>")
@login_required
def blog_post(post_id):
    post = Post.query.get_or_404(post_id)
    if not current_user.is_authenticated:
        flash("You need to log in to access this page")
        return redirect(url_for("home"))
    return render_template("blog_post.html", title=f"{post.title}", post=post)


@app.route("/new_post", methods=["GET", "POST"])
@login_required
def new_post():
    form = NewPostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("new_post.html", title="New Post", form=form)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        return render_template("blog_post.html", title=f"{current_user} - {post.title}", post=post)
    form = NewPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return redirect(url_for("home", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("update_post.html", title="Update Post", post=post, form=form)


@app.route("/post/<int:post_id>/delete")
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted.")
    return redirect(url_for("home"))


@app.route("/user-posts/<username>")
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    user_posts = Post.query.filter_by(author=user).all()
    return render_template("user_posts.html", user_posts=user_posts, user=user, title=f"{user.username} posts")