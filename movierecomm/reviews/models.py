from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
import numpy as np
# Create your models here.

class Movie(models.Model):
    movieId = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=256)
    genres = models.CharField(max_length=256, null=True)

    def __str__(self):
        return "{title:\"%s\",genres:\"%s\", rating:%, id:%d}"  %(self.user.username, self.movie.title, self.ratin, self.movieId)

    def average_rating(self):
        all_ratings = map(lambda x:x.rating, self.review_set.all())
        return np.mean(all_ratings)


class Review(models.Model):
    RATING_CHOICES = (
            (0, '0'),
            (1, '1'),
            (2, '2'),
            (3, '3'),
            (4, '4'),
            (5, '5'),
    )
    user = models.ForeignKey(User)
    movie = models.ForeignKey(Movie)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.CharField(max_length=1024, null=True)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return "{user:\"%s\",movie:\"%s\", rating:%d, id: %d}"  %(self.user.username, self.movie.title, self.rating, self.id)

    class Meta:
        unique_together = (('user', 'movie'),)

class RecommendedMovieList(models.Model):
    user = models.ForeignKey(User)
    movie = models.ForeignKey(Movie)
    priority = models.IntegerField()

    ALGO_CHOICES = (
            ('KMEAN', 'KMEAN'),
            ('KNN', 'KNN'),
    )

    algo = models.CharField(max_length=128, default='NAIVE')

    def __str__(self):
        return "{user:\"%s\",movie:\"%s\", priority:%d, algo:%s}"  %(self.user.username, self.movie.title, self.priority, self.algo)

    class Meta:
        unique_together = (('user', 'movie', 'algo'),)

