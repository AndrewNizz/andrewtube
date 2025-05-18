from flask import Blueprint, render_template, request, jsonify, make_response, redirect, flash
import db_session
from models import Users


users_blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@users_blueprint.route('/user/register', methods=['GET', 'POST'])
def register():
    db_session.global_init('../data/static/users.db')
    sess = db_session.create_session()
    if request.method == 'POST':
        form = request.form
        confirm_password = form['confirm_password']

        if form['password'] != confirm_password:
            flash('Пароли не совпадают!', 'error')
            return render_template('register_form.html', form=form, title='Create an account')

        existing_user = sess.query(Users).filter(Users.email == form['email']).first()
        if existing_user:
            flash('Пользователь с таким email уже существует!', 'error')
            return render_template('register_form.html', form=form, title='Create an account')

        new_user = Users()
        new_user.set_password(form['password'])
        new_user.email = form['email']
        new_user.name = form['username']
        sess.add(new_user)
        sess.commit()

        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect('/')
    elif request.method == 'GET':
        return render_template('register_form.html', title='Create an account')


@users_blueprint.route('/user/update/<int:user_id>', methods=['POST'])
def update_user_data(user_id):
    return redirect('/')


@users_blueprint.route('/user/delete/<int:user_id>')
def delete_user(user_id):
    db_session.global_init('../data/static/users.db')
    sess = db_session.create_session()
    res = sess.query(Users).get(user_id)
    sess.delete(res)
    sess.commit()
    return redirect('/')

