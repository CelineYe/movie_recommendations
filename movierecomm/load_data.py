#!/usr/bin/env python

import sys, os 
import traceback
import pandas as pd

import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movierecomm.settings")

import django
django.setup()

from django.contrib.auth.models import User
from reviews.models import Review, Movie


def save_user_from_row(row):
    user = User()
    user.id = row['userId']
    user.username = row['userId']
    user.is_active = False
    try:
        user.save()
    except Exception as e:
        print "row:", row, "\nexceptoin:", e, "\ntraceback:", traceback.format_exc()
        exit(0)
   
def save_review_from_row(row):
    try:
        review = Review.objects.get(user_id=row['userId'], movie_id=row['movieId'])
        review.rating = row['rating']
        review.save(update_fields=['rating'])

    except Review.DoesNotExist :
        review = Review()
        review.user = User.objects.get(id = row['userId'])
        review.movie = Movie.objects.get(movieId = row['movieId'])
        review.rating = row['rating']
        review.pub_date = datetime.datetime.fromtimestamp(row['timestamp'])
        review.save()


def save_movie_from_row(row):
    movie = Movie()
    movie.movieId = row['movieId']
    movie.title = row['title']
    movie.genres = row['genres']
    movie.save()
#    print 'saving movieId:', movie.movieId

def load_users(filename = 'data/ratings.csv'):
    ratings_df = pd.read_csv(filename)
    for idx, row in ratings_df.iterrows():
        if idx % 100 == 0:
            print idx, "userId:", row['userId']
        save_user_from_row(row)

def load_ratings(filename = 'data/ratings.csv'):
    ratings_df = pd.read_csv(filename)

    for idx, row in ratings_df.iterrows():
        if idx % 100 == 0:
            print idx, "ratings:", row['userId'], row['movieId']
        save_review_from_row(row)


def load_movies(filename = 'data/movies.csv'):
    movies_df = pd.read_csv(filename)
#    movies_df.apply( save_movie_from_row, axis = 1)
    for idx, row in movies_df.iterrows():
        if idx % 100 == 0 :
            print idx,'saving movie:', row['movieId'], ":",  row['title']
        save_movie_from_row(row)
        

def load_data():
#   load_movies()
#   load_users()
   load_ratings()

if __name__ == "__main__":
    load_data()
