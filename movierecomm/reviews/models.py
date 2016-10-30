from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
import numpy as np
# Create your models here.

class Movie(models.Model):
    movieId = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=256)
    genres = models.CharField(max_length=256)

    def average_rating(self):
        all_ratings = map(lambda x:x.rating, self.review_set.all())
        return np.mean(all_ratings)

class Rating(models.Model):
    RATING_CHOICES = (
            (0, '0'),
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '4'),
    )
    userId = models.ForeignKey(User)
    movieId = models.ForeignKey(Movie)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.CharField(max_length=1024)
    timestamp = models.IntegerField()

class RecommendedMovieList(models.Model):
    user = models.ForeignKey(User)
    movie = models.ForeignKey(Movie)
    priority = models.IntegerField()

