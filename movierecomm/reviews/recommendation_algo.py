
from django.contrib.auth.models import User
from reviews.models import Review, Movie

#--- algo callback
def update_recommendation_by_review(record, mode):
    """ record: (userId, movieId)
    mode: add, update, delete """
    print 'update_recommendation_by_review:', record, mode
    return 
    #--- read from db -----
    allreviews = Review.objects.all() # review.movie_id, review.user_id, review.rating

    #--- computing ------
#    df = DataFrame()
    for review in allreviews:
        print review.movie.movieId, review.user.id, review.rating

    return
    #--- write to db -----
    allusers = User.objects.all()
    for user in allusers:
        recomm = RecommendedMovieList()
        recomm.user_id = 10
        recomm.movie_id = 10
        recomm.priority = 10  # 0..100
        recomm.algo = 'KNN'
#        recomm.save()

