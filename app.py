import datetime
import random

import flask
import urllib
import pathlib
import records
from flask_sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)

# ------------------------------------------------------------------------------
# Database configuration, which includes definition for database connectors
# initialization for models, and creation of tables
# ------------------------------------------------------------------------------

DATABASE_URL = 'sqlite:////' + str(pathlib.Path(__file__).parent / 'test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# SQLAlchemy wrapper around the database connection
db = SQLAlchemy(app)

# Records (https://pypi.org/project/records/) interface around it
rec = records.Database(DATABASE_URL)


# SQLAlchemy model to work withe
class Completed(db.Model):
    task_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    user_id = db.Column(db.Integer, nullable=False)
    completed_date = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


db.create_all()

# ------------------------------------------------------------------------------
# Controllers
# ------------------------------------------------------------------------------


@app.route('/')
def index():
    """
    Main function which accepts parameters in querystring, and returns the
    HTML page which shows three last records with the link to previous
    three objects.

    Previous page has to contain the link returning three records before that,
    etc.
    """
    # dict of GET arguments. We currently don't use it anywhere
    args = dict(flask.request.args)
    try:
        page = int(args.get('page', 1))
        completed_date_epoch = int(args.get('completed_date', datetime.datetime.utcnow().timestamp()))
    except ValueError:
        page = 1
        completed_date_epoch = datetime.datetime.utcnow().timestamp()
    
    completed_date = datetime.datetime.fromtimestamp(completed_date_epoch)

    # get the set of tasks
    tasks = Completed.query.filter_by(user_id=get_uid()).filter(
        Completed.completed_date<=completed_date).order_by(
            Completed.completed_date.desc()).paginate(page, 3, False)

    # equal variant for raw SQL
    # tasks = rec.query(f'''
    #    where user_id = {get_uid()}
    #    order by completed_date desc limit 3
    # ''')

    # next URL
    query_string = {'page': page+1, 'completed_date': completed_date_epoch}
    next_url = f'/?{urllib.parse.urlencode(query_string)}'

    return flask.render_template('tasks.html', tasks=tasks.items, next_url=next_url)


@app.route('/init')
def init():
    """
    Helper function which populates the database with stub values
    """
    def _add(task_id, content, hh, mm):
        completed_date = datetime.datetime(2019, 1, 1, hh, mm, 0)
        obj = Completed(
            user_id=get_uid(),
            task_id=task_id,
            content=content,
            completed_date=completed_date)
        db.session.add(obj)

    # First three tasks were completed around 2am
    _add(1, "A1", 2, 0)
    _add(11, "A2", 2, 10)
    _add(101, "A3", 2, 20)
    # These tasks were completed earlier, around 1am
    _add(2, "B1", 1, 0)
    _add(12, "B2", 1, 10)
    _add(102, "B3", 1, 20)
    # Lately, following three tasks were completed exactly ad midnight
    _add(3, "C1", 0, 0)
    _add(13, "C2", 0, 0)
    _add(103, "C3", 0, 0)
    db.session.commit()
    return flask.redirect('/')


@app.route('/reset')
def reset():
    """
    Helper function which resets the database
    """
    Completed.query.delete()
    db.session.commit()
    return flask.redirect('/init')


@app.route('/add')
def add():
    """
    Helper function which resets the database
    """
    task_id = random.randint(1, 100000)
    obj = Completed(
        user_id=get_uid(),
        task_id=task_id,
        content=f'X{task_id}',
        completed_date=datetime.datetime.utcnow())
    db.session.add(obj)
    db.session.commit()
    return flask.redirect('/')


def get_uid():
    """
    Authorization function which returns the current user_id for the user.
    In our case it always returns 1
    """
    return 1
