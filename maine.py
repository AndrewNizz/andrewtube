from flask import Flask, redirect, render_template, make_response, jsonify, request, flash, send_file
from flask_login import login_user, login_required, current_user, LoginManager
from data import db_session
from models import Videos, Users
from video_api import blueprint
from user_api import users_blueprint
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'YANDEX_LYCEUM_SECRET_KEY'
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_POOL_SIZE'] = 20
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 15
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Users).get(user_id)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/get_video_preview/<int:video_id>')
def get_video_preview(video_id):
    sess = db_session.create_session()
    vid = sess.query(Videos).get(video_id)
    return send_file(BytesIO(vid.preview), mimetype='image/jpg')


@app.route('/get_video_file/<int:video_id>')
def get_video_file(video_id):
    sess = db_session.create_session()
    vid = sess.query(Videos).get(video_id)
    return send_file(BytesIO(vid.link), mimetype='video/mp4', conditional=True, as_attachment=False)


@app.route('/', methods=['GET', 'POST'])
def get_videoss():
    sess = db_session.create_session()
    if request.method == 'GET':
        vids = sess.query(Videos).all()
        return render_template('index.html', videos=vids, current_user=current_user, titl='AndrewTube')


@app.route('/user/login', methods=['GET', 'POST'])
def login_user():
    sess = db_session.create_session()
    if request.method == 'POST':
        form = request.form
        email = form['email']
        password = form['password']

        user = sess.query(Users).filter(Users.email == email).first()

        if user and user.check_password_hash(user.password, password):
            login_user(user, remember=bool(form['remember_me']))
            print('-------- Я вошел ----------------------------------------------------------------------------------')
            flash('Успешный вход!', 'success')
            return redirect('/')
        else:
            flash('Неверный email или пароль', 'error')
            return render_template('login_form.html', title='Login')

    return render_template('login_form.html', title='Login')


def main():
    db_session.global_init('../data/static/users.db')
    app.register_blueprint(blueprint)
    app.register_blueprint(users_blueprint)
    app.run(host='127.0.0.1', port=8080)


if __name__ == '__main__':
    main()
