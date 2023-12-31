from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

Bootstrap5(app)

db = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies-collection.db"

db.init_app(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

with app.app_context():
    db.create_all()

class EditForm(FlaskForm):
    rating = StringField('Your Rating Out of 10',validators=[DataRequired()])
    review = StringField('Your Review',validators=[DataRequired()])
    submit = SubmitField('Done')

class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])    
    submit = SubmitField('Add Movie')

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )

# second_movie = Movie(
#     title="Avatar The Way of Water",
#     year=2022,
#     description="Set more than a decade after the events of the first film, learn the story of the Sully family (Jake, Neytiri, and their kids), the trouble that follows them, the lengths they go to keep each other safe, the battles they fight to stay alive, and the tragedies they endure.",
#     rating=7.3,
#     ranking=9,
#     review="I liked the water.",
#     img_url="https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
# )

# with app.app_context():
#     db.session.add(new_movie)
#     db.session.add(second_movie)
#     db.session.commit()
API_KEY = "c3d573c35fab0c58ec25001a467a0892"

@app.route("/")
def home():
    movies = db.session.execute(db.select(Movie).order_by(Movie.rating)).scalars().all()
    for i in range(len(movies)) :
        movies[i].ranking = len(movies) - i
    return render_template("index.html", movies = movies )

@app.route("/edit",methods=['GET','POST'])
def edit():
    form = EditForm()
    if form.validate_on_submit():
        id = request.args.get('id')
        movie = db.get_or_404(Movie, id)
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form = form, title = request.args.get('title'))


@app.route('/delete')
def delete():
    id = request.args.get('id')
    movie = db.get_or_404(Movie, id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add', methods = ['GET','POST'])
def add():
    form = AddForm()

    if form.validate_on_submit():
        params = {
            'query' : form.title.data,
            'api_key' : API_KEY,
        }
        response = requests.get("https://api.themoviedb.org/3/search/movie", params=params)
        response.raise_for_status()
        return render_template('select.html', movie_list = response.json()['results'])
    return render_template('add.html', form = form)

@app.route("/select")
def select():
    id = request.args.get('id')
    url = f"https://api.themoviedb.org/3/movie/{id}"
    response = requests.get(url, params={"api_key": API_KEY})
    details = response.json()
    movie = Movie(
        title = details["title"],
        year = details["release_date"].split("-")[0],
        description = details["overview"],
        img_url = f"https://image.tmdb.org/t/p/original{details['poster_path']}"
    )
    db.session.add(movie)
    db.session.commit()
    return redirect(url_for('edit', id = movie.id, title = details['title']))

if __name__ == '__main__':
    app.run(debug=True)
