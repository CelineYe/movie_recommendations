from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import Review, Movie, RecommendedMovieList
from .forms import ReviewForm
from .recommendation_algo import update_recommendation_by_review
import datetime

from django.contrib.auth.decorators import login_required
# Create your views here.

def review_list(request):
    latest_review_list = Review.objects.order_by('-pub_date')[:6] #.values('user__username', 'movie__title', 'rating','comment')
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
    movie = get_object_or_404(Movie, pk=movie_id)
    form = ReviewForm()
    return render(request, 'reviews/movie_detail.html', {'movie':movie, 'form':form})

@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating = form.cleaned_data['rating']
        comment = form.cleaned_data['comment']
        try:
            review = Review.objects.get(user_id=request.user.id, movie_id=movie_id)
            review.rating = rating
            review.save(update_fields=['rating', 'comment'])
            update_recommendation_by_review((request.user.id, movie_id), 'update')
        except Review.DoesNotExist :
            review = Review()
            review.movie = movie
            review.user = request.user
            review.rating = rating
            review.comment = comment
            review.pub_date = datetime.datetime.now()
            review.save()
            update_recommendation_by_review((request.user.id, movie_id), 'add')
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:movie_detail', args=(movie.movieId,)))
    
    return render(request, 'reviews/movie_detail.html', {'movie': movie, 'form': form})
    

def user_review_list(request, userid=None):
    if not userid:
        userid = request.user.id
    latest_review_list = Review.objects.filter(user__id=userid).order_by('-pub_date')
    context = {'latest_review_list':latest_review_list, 'username':request.user.username}
    return render(request, 'reviews/user_review_list.html', context)


@login_required
def user_recommendation_list(request):
    recomm = RecommendedMovieList.objects.filter(user_id=request.user.id).order_by('priority').prefetch_related('movie')[:10]
    movie_list = [] # [r.movie for r in recomm]
    for m in recomm:
        m.movie.priority = m.priority
        m.movie.algoName = m.algo
        movie_list.append(m.movie)

    return render(
        request, 
        'reviews/recommendation_list.html', 
        {'username': request.user.username,'movie_list': movie_list}
    )
    



