from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import Review, Movie, RecommendedMovieList
from .forms import ReviewForm

import datetime

from django.contrib.auth.decorators import login_required
# Create your views here.

def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:9]
    context = {'latest_review_list':latest_review_list}
    return render(request, 'reviews/review_list.html', context)


def review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'reviews/review_detail.html', {'review': review})


def movie_list(request):
    movie_list = Movie.objects.order_by('-title')
    context = {'movie_list':movie_list}
    return render(request, 'reviews/movie_list.html', context)


def movie_detail(request, movie_id):
    pass

@login_required
def add_review(request, movie_id):
    pass
    

def user_review_list(request, userid=None):
    pass


@login_required
def user_recommendation_list(request):
    pass


