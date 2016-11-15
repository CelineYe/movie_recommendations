import os
from django.contrib.auth.models import User
from reviews.models import Review, Movie, RecommendedMovieList
import numpy as np

from jz_naive_recommendation_algo import jz_calculate_recommendations


_debug = True

def printMsg(*args):
    if _debug: print args


def scaleRating(r):
    """ scale rating from [u,v] to range [x, y]
    """
    u, v = 0.0, 5
    x, y = 10.0, 100
    return x + (r-u) *(y-x)/(v-u)

def save_recommendation(algoName, records):
    """ save into database:
    records: {userId:[(movieId, prioriy)]} 
    """
    printMsg( "saving recommendations for algo:", algoName, len(records) )

    RecommendedMovieList.objects.filter(algo=algoName).delete()
    for userId, recList in records.iteritems():
        for m in recList:
            if RecommendedMovieList.objects.filter(user_id = userId, movie_id = m[0], priority = m[1], algo=algoName).count() > 0:
                continue
            r = RecommendedMovieList(user_id = userId, movie_id = m[0], priority = m[1], algo=algoName)
            printMsg(r)
            r.save()

#--- algo callback -----------------------------------------
def update_recommendation_by_review(record=None, mode=None):
    """ record: (userId, movieId)
    mode: add, update, delete """
    print 'update_recommendation_by_review:', record, mode
     
    #--- read from db -----
    allreviews = Review.objects.all() # review.movie_id, review.user_id, review.rating
    userCount = User.objects.count()
    movieCount = Movie.objects.count()
    printMsg("userCount:", userCount, "movieCount:", movieCount)

    uidmap = {} # {index:id}
    uidrmap = {} #{id:index}
    midmap = {}
    midrmap = {}
    ratings = np.full((userCount, movieCount), np.inf)  # user rating matrix
    NU = NM = 0
    for r in allreviews:
        uid, mid = r.user_id, r.movie_id
        if uidrmap.has_key(uid):
            ui = uidrmap[uid]
        else:
            ui = NU
            uidmap[ui] = uid
            uidrmap[uid] = ui
            NU += 1

        if midrmap.has_key(mid):
            mi = midrmap[mid]
        else:
            mi = NM
            midmap[mi] = mid
            midrmap[mid] = mi
            NM += 1
        ratings[ui, mi] = scaleRating(float(r.rating))

    printMsg("admin:",  User.objects.get(id=669).username, uidrmap[669], "movie:", 2550, midrmap[2550] )

    #--- computing in different algorithms ------
    algos = [('JZNAIVE', jz_calculate_recommendations)]
    for a in algos:
        ru = a[1](ratings, userCount, movieCount, NU, NM)
        rec = {}   # { userId: [ (movieId, priority) ]}
        for uidx, m  in ru.iteritems():
            t = rec[ uidmap[uidx] ] = []
            for mi in m:
                t.append( (midmap[mi[0]], mi[1]) )
        save_recommendation(a[0], rec)


if __name__ == '__main__':
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "../movierecomm.settings")

    django.setup()
    update_recommendation_by_review(None, None)


