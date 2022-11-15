from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import os

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,FloatField
from wtforms.validators import DataRequired ,NumberRange
import requests
#####################################################








######################################################
directory = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///'+os.path.join(directory,"data.sqlite")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Bootstrap(app)

app.app_context().push()

class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String,unique=True,nullable=False)
    year = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String,nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String)
    img_url = db.Column(db.String,nullable=False)

class EditForm(FlaskForm):
    rating = FloatField("Your rating out of 10 e.g 7.5",validators=[NumberRange(min=0,max=10),DataRequired()])
    review = StringField("Your Review",validators=[DataRequired()])
    submit = SubmitField("Submit Rating")

class AddForm(FlaskForm):
    title = StringField("Movie Title You want Add")
    submit = SubmitField("Search Movie")
# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
#
# db.create_all()
# db.session.add(new_movie)
# db.session.commit()

# all_movies = db.session.query(Movie).all()
# print(all_movies)


@app.route("/")
def home():
    all_movies = db.session.query(Movie).order_by(-Movie.rating)
    # print(all_movies)
    order = 1
    for movie in all_movies:
        movie.ranking = order
        order += 1
    db.session.commit()
    return render_template("index.html",movies=all_movies)


@app.route("/delete")
def delete():
    movieid = request.args.get("id")
    movie_delete = Movie.query.filter_by(id=movieid).first()
    db.session.delete(movie_delete)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit",methods=["GET","POST"])
def Edit():
    form = EditForm()
    movieid = request.args.get("id")
    movie_Edited = Movie.query.filter_by(id=movieid).first()
    if form.validate_on_submit():
        movie_Edited.rating = form.rating.data
        movie_Edited.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html",form=form)

@app.route("/add",methods=["GET","POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_searched = form.title.data
        url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key":  os.environ.get("MOVIE_API_KEY"), "query": movie_searched}
        response = requests.get(url=url, params=params)
        searched_movies = response.json()["results"]
        # print(searched_movies)
        return render_template("select.html",movies=searched_movies)
    return render_template("add.html",form=form)


@app.route("/add2",methods=["GET","POST"])
def add2():
    all_movies = db.session.query(Movie).all()
    movie_id = request.args.get("id")
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": os.environ.get("MOVIE_API_KEY") }
    response = requests.get(url=url,params=params)
    result = response.json()
    # https://image.tmdb.org/t/p/w500/
    url_img = f"https://image.tmdb.org/t/p/w500/{result['poster_path']}"
    title = result["original_title"]
    year = result["release_date"]
    description = result["overview"]
    new_movie = Movie(title=title, year=year, description=description, img_url=url_img)
    db.session.add(new_movie)
    db.session.commit()

    movie_edit = Movie.query.filter_by(title=title).first()
    movie_id = movie_edit.id

    all_movies = db.session.query(Movie).all()
    return redirect(url_for("Edit",id=movie_id))


@app.route("/select")
def select():
    return render_template("select.html")

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
