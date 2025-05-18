from flask import Blueprint, render_template, request, jsonify, make_response, redirect, send_file, flash
import db_session
from models import Videos, Comments
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import SubmitField, StringField, FileField
from wtforms.validators import DataRequired
import datetime
from io import BytesIO


class AddVideoForm(FlaskForm):
    video_title = StringField('Название видео', validators=[DataRequired()])
    video_file = FileField('Видео файл', validators=[DataRequired()])
    preview_im = FileField('Превью видео')
    btn = SubmitField('Загрузить', validators=[DataRequired()])


blueprint = Blueprint(
    "videos_api",
    __name__,
    template_folder="templates"
)


@blueprint.route('/', methods=['GET', 'POST'])
def get_videos():
    db_session.global_init('../data/static/users.db')
    filter_words = request.form['user_input']
    sess = db_session.create_session()
    vids = sess.query(Videos).filter(Videos.title.like(f'%{filter_words}%'))
    return render_template('index.html', videos=vids, titl=f'Found videos for request {filter_words}', current_user=current_user)


@blueprint.route('/video/get/<int:video_id>', methods=['GET', 'POST'])
def get_video(video_id):
    db_session.global_init('../data/static/users.db')
    sess = db_session.create_session()
    if request.method == 'GET':
        res = sess.query(Videos).get(video_id)
        if not res:
            return make_response(jsonify({'error': 'Not found'}), 404)
        else:
            comms = sess.query(Comments).filter(Comments.video_id == video_id)
            return render_template('one_video.html', vid=res, comments=comms, current_user=current_user)
    elif request.method == 'POST':
        if request.form and current_user.is_authenticated:
            comm = request.form['comment-text']
            new_comm = Comments(comment=comm, author=current_user.id, video_id=video_id)
            sess.add(new_comm)
            sess.commit()
            return redirect(f'/video/get/{video_id}')
        else:
            return redirect('/user/login')


@blueprint.route('/video/add', methods=['POST'])
def create_video():
    db_session.global_init('../data/static/users.db')
    form = AddVideoForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        sess = db_session.create_session()
        title, video_file, preview = form.video_title, form.video_file, form.preview_im
        new = Videos(title=title,
                     author=current_user.id,
                     link=video_file,
                     preview=preview,
                     comments='',
                     views=0,
                     created_date=datetime.datetime.today().date())
        sess.add(new)
        sess.commit()
        if request.accept_mimetypes.accept_json:
            return jsonify({'seccess': 'OK'})
        return redirect("/")


@blueprint.route('/video/add', methods=['GET'])
def create_video_page():
    if not current_user or not current_user.is_authentificated:
        flash('To create a video you need to log in', 'error')
        return redirect('/user/login')
    else:
        form = AddVideoForm()
        return render_template('create_video.html', form=form)


@blueprint.route('/video/author/<int:user_id>', methods=['GET'])
def get_videos_for_user(user_id):
    db_session.global_init('../data/static/users.db')
    sess = db_session.create_session()
    res = sess.query(Videos).filter(Videos.author == user_id)
    return render_template('users_videos.html', vids=res)


@blueprint.route('/video/delete/<int:video_id>')
def delete_video(video_id):
    db_session.global_init('../data/static/users.db')
    sess = db_session.create_session()
    res = sess.query(Videos).get(video_id)
    sess.delete(res)
    sess.commit()
    return redirect('/')

