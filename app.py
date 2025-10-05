from flask import Flask, render_template, redirect, url_for, flash
from config import Config
from models import db, User
from forms import UserForm


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
        return render_template('list.html', users=users)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
