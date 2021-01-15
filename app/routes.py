import config, os, uuid, base64, time
from flask import render_template, flash, redirect, url_for, request, abort, send_from_directory, current_app
from app import  app, db, login
from app.forms import LoginForm, RegistrationForm, PostForm, FileForm, ResetPasswordRequestForm, ResetPasswordForm, EncryptedNotesForm, DecrypytNotesForm
from app.utils import send_password_reset_email, generate_fernet_key
from app.models import User, Post, PrivPost, File, EncryptedNote
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Udało się zarejestrować!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    public_posts = Post.query.filter_by(public=1).all()
    private_posts = Post.query.join(PrivPost, (PrivPost.post_id == Post.id)).filter(PrivPost.user_id == current_user.id).all()
    return render_template('user.html', user=user, public_posts=public_posts, private_posts=private_posts)

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user, priv_recipient=form.priv_recipient.data, public=form.public.data)
        db.session.add(post)
        db.session.commit()
        if form.priv_recipient.data != '':
            user = User.query.filter_by(username=form.priv_recipient.data).first_or_404()
            priv = PrivPost(priv_post=post, recipient=user)
            db.session.add(priv)
            db.session.commit()
        flash('Post dodany!')
        return redirect(url_for('index'))
    return render_template('postform.html', title='Post', form=form)

@app.route('/upload', methods=['GET','POST'])
@login_required
def upload_file():
    form=FileForm()
    if request.method == 'POST':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        uid = str(uuid.uuid4())
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in ['.txt', '.pdf', '.PNG', '.jpg', '.jpeg', '.gif']:
                abort(400)
            uid = uid+file_ext
            uploads = os.path.join(current_app.root_path, 'uploads')
            uploaded_file.save(os.path.join(uploads, uid))
            f = File(file_name=filename, owner=current_user, uuid=uid)
            db.session.add(f)
            db.session.commit()
            flash('Plik dodany!')
            return redirect(url_for('index'))
    return render_template('file_upload.html', title='Upload', form=form)

@app.route('/uploads/<filename>')
@login_required
def upload(filename):
    uploads = os.path.join(current_app.root_path, 'uploads')
    return send_from_directory(uploads, filename)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Instrukcja została wysłana na maila')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/post_encrypted', methods=['GET','POST'])
@login_required
def post_encrypted():
    form = EncryptedNotesForm()
    if form.validate_on_submit():
        password = form.password.data
        salt = os.urandom(16)
        key = generate_fernet_key(password, salt)
        fer = Fernet(key)
        note = fer.encrypt(form.post.data.encode())
        uid = str(uuid.uuid4())
        filename = uid + '.txt'
        notes = os.path.join(current_app.root_path, 'notes')
        f = open(os.path.join(notes, filename), 'wb')
        f.write(note)
        f.close
        e_n = EncryptedNote(file_id=filename, salt=salt)
        e_n.set_password(password)
        db.session.add(e_n)
        db.session.commit()
        flash('Udało się zapisać zaszyfrowaną notatkę, zapisz unikalny numer notatki, w przeciwnym wypadku nie będziesz w stanie jej odzyskać: ' + uid)
        return redirect(url_for('index'))
    return render_template('encryptedpostform.html', form=form)

@app.route('/decrypt_post', methods=['GET','POST'])
@login_required
def decrypt_post():
    form = DecrypytNotesForm()
    if form.validate_on_submit():
        file_id = form.note_id.data + '.txt'
        note = EncryptedNote.query.filter_by(file_id=file_id).first()
        if note is None or not note.check_password(form.password.data):
            time.wait(3)
            flash('Błędny numer notatki lub hasło')
            return redirect(url_for('decrypt_post'))
        password = form.password.data
        salt = note.salt
        key = generate_fernet_key(password, salt)
        fer = Fernet(key)
        notes = os.path.join(current_app.root_path, 'notes')
        f = open(os.path.join(notes, file_id), 'rb')
        token = f.readlines()[0]
        decrypted = fer.decrypt(token)
        f.close()
        flash('Treść twojej notatki: ' + decrypted.decode())
        return redirect(url_for('index'))
    return render_template('decrypt_post.html', form=form)
