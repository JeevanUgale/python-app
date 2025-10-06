import os
from flask import Flask, render_template, redirect, url_for, flash
from .config import Config
from .models import db, User
from .forms import UserForm


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/', methods=['GET', 'POST'])
    def index():
        form = UserForm()
        if form.validate_on_submit():
            user = User(
                first_name=form.first_name.data.strip(),
                last_name=form.last_name.data.strip(),
                age=form.age.data,
                qualification=(form.qualification.data or '').strip(),
                address=(form.address.data or '').strip(),
            )
            db.session.add(user)
            db.session.commit()
            flash('User saved successfully', 'success')
            return redirect(url_for('list_users'))
        return render_template('index.html', form=form)

    @app.route('/users')
    def list_users():
        users = User.query.order_by(User.id.desc()).all()
        from .forms import DeleteForm
        delete_form = DeleteForm()
        return render_template('list.html', users=users, delete_form=delete_form)


    @app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
    def edit_user(user_id):
        user = User.query.get_or_404(user_id)
        form = UserForm(obj=user)
        if form.validate_on_submit():
            user.first_name = form.first_name.data.strip()
            user.last_name = form.last_name.data.strip()
            user.age = form.age.data
            user.qualification = (form.qualification.data or '').strip()
            user.address = (form.address.data or '').strip()
            db.session.commit()
            flash('User updated successfully', 'success')
            return redirect(url_for('list_users'))
        return render_template('edit.html', form=form, user=user)


    @app.route('/users/<int:user_id>/delete', methods=['POST'])
    def delete_user(user_id):
        form = None
        try:
            from .forms import DeleteForm
            form = DeleteForm()
        except Exception:
            pass
        # Validate CSRF if form present
        if form and not form.validate_on_submit():
            flash('Invalid delete request', 'danger')
            return redirect(url_for('list_users'))
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash('User deleted', 'success')
        return redirect(url_for('list_users'))

    return app


def run():
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = app.config.get('DEBUG', False)
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run()
