import os
from django.contrib.auth.models import User
from reviews.models import Review, Movie, RecommendedMovieList

import numpy as np
from operator import itemgetter, add

_debug = True

def printMsg(*args):
    if _debug: print args

def valid_numeric(x):
    return not np.isinf(x) and not np.isnan(x)

def square(x):
    return x*x

def square_diff(x,y):
    d = x-y
    return d*d

def counted_func(mutable_counter, func):
    def f(*args):
        mutable_counter[0] += 1
        return add(*args)
    return f

def defPreBinaryFunc(preFunc, binFunc):
    def f(x,y):
        preFunc()
        return binFunc(x,y)
    return f

def foreach_in_row(A, I, func, reduceFunc=None, initial=0):
    N = A.shape[1]
    if reduceFunc:
        for k in xrange(N):
            if valid_numeric(A[I,k]):
                initial = reduceFunc(initial, func(A[I, k]))
        return initial
    else:
        for k in xrange(N):
            if valid_numeric(A[I,k]):
                func(A[I, k])

def foreach_in_col(A, I, func, reduceFunc=None, initial=0):
    N = A.shape[0]
    if reduceFunc:
        for k in xrange(N):
            if valid_numeric(A[k, I]) : initial = reduceFunc(initial, func(A[k, I]))
        return initial
    else:
        for k in xrange(N):
            if valid_numeric(A[k, I]) : func(A[k, I])

def foreach_pair_rows(A, I, J, func, reduceFunc=None, initial=0):
    """ call func(A[I, k], A[J, k] if A[i] and B[i] are valid 
    """
    N = A.shape[1]
    if reduceFunc :
        for k in xrange(N):
            if valid_numeric(A[I,k]) and valid_numeric(A[J,k]):
                initial = reduceFunc(initial, func(A[I, k], A[J, k]))
        return initial
    else:
        for k in xrange(N):
            if valid_numeric(A[I,k]) and valid_numeric(A[J,k]):
                func(A[I,k], A[J,k])

def square_distance(A, I, J):
    """ A[I,:] and A[J,:] distance. 
    return (distance, nDim)  # nDim: number of calculated dimensions
    """
    nDim = [0]
    d = foreach_pair_rows(A, I, J, square_diff, counted_func(nDim, add), 0.0)
    return (d, nDim[0])

def cosine_distance(A, I, J):
    nDim = [0]
    dot = foreach_pair_rows(A, I, J, lambda x, y: x*y, counted_func(nDim, add), 0.0)
    if nDim[0] > 0 :
        d1 = foreach_in_row(A, I, square, add, 0.0)
        d2 = foreach_in_row(A, J, square, add, 0.0)
        d = dot/d1*dot/d2
        if d == 0 :
            printMsg( "zero:", dot, d1, d2, nDim[0] )
            printMsg( "zero I:", A[I,:] )
            printMsg( "zero J:", A[J,:] )
        return (d, nDim[0])
    else:
        return (np.inf, nDim[0])


def scaleRating(r):
    """ scale rating from [u,v] to range [x, y]
    """
    u, v = 0.0, 5
    x, y = 10.0, 100
    return x + (r-u) *(y-x)/(v-u)

def jz_calculate_recommendations(ratings, userCount, movieCount, NU, NM, MAX_RECOMM=5):
    """ ratings[u, m]: movie i rating by user u
    userCount, movieCount: number of users and movies
    Nu, NM : valid number of users and movies. all the reset are set numpy.inf

    return recommededMovies: { userIndex: [(movieIndex, priority) ] } .
    """

    # todo scale rating to range [r0, r1], so that distance is not zero
    printMsg("Ratings:", ratings.shape, ratings[17, 669])

    #-- most popular movie index
    ratings_by_movie = [] # [ (movieIndex, rating) ]
    for i in xrange(NM):
        ratings_by_movie.append((i, foreach_in_col(ratings, i, lambda x:x, add, 0.0)))

    ratings_by_movie = sorted(ratings_by_movie, key=itemgetter(1))

    printMsg("Most popular movie:",  ratings_by_movie[0])

    #-- calculate distances between users
    du = np.full((userCount,userCount), np.inf)
    for i in xrange(NU-1):
        for k in xrange(NU-i-1):
            j = i+k+1
            d, nDim = cosine_distance(ratings, i, j) # alternative : cosine distance, square distance
            if nDim > 0: du[i,j] = du[j, i] = d      # ensure du is not zero

    printMsg("user distance Matix:", du)

    #-- recommendations for users
    if MAX_RECOMM > NM: MAX_RECOMM = NM

    ru = {}   # recommended MovieId : { userIndex: [(movieIndex, priority)] }
    for i in xrange(NU):
        wr = [] # [(movieIndex, rating)]: weighted rating for each movie
        for m in xrange(NM):
            if valid_numeric(ratings[i, m]):  #  skip that user watched already.
                continue
            r = 0.0
            n = 0  # count valid ratings by similar users
            for j in xrange(NU):
                if valid_numeric(du[i,j]) and valid_numeric(ratings[j, m]) :
                    r += ratings[j, m] / du[i,j]
                    n += 1
            if n > 0: 
                wr.append((m, r))
        sortedMi = sorted(wr, key=itemgetter(1), reverse=True)  # sort by rating
        n = len(sortedMi)
        if n > MAX_RECOMM: n = MAX_RECOMM
        if n > 0:
            ru[i] = wr[:n]
        # todo : if no recommended movies, select most populars or randomly pick up some
#        printMsg("recommended: ", i, ru[i])
    return ru

def save_recommendation(algoName, records):
    """ save into database:
    records: {userId:[(movieId, prioriy)]} 
    """
    printMsg( "saving recommendations for algo:", algoName, len(records) )

    RecommendedMovieList.objects.filter(algo=algoName).delete()
    for userId, recList in records.iteritems():
        for m in recList:
            if RecommendedMovieList.objects.get(user_id = userId, movie_id = m[0], priority = m[1]) :
                continue
            r = RecommendedMovieList(user_id = userId, movie_id = m[0], priority = m[1])
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


