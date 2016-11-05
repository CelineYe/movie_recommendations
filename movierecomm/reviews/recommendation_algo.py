
from django.contrib.auth.models import User
from reviews.models import Review, Movie

import numpy as np
from operator import itemgetter

_debug = False

def printMsg(*args):
    if _debug: print args

def valid_numeric(x):
    return not np.isinf(x) and not np.nan(x)

def add(x, y):
    return x+y

def max(x, y):
    return x if x > y else y

def square_diff(x,y):
    d = x-y
    return d*d

def defPreBinaryFunc(preFunc, binFunc):
    def f(x,y):
        preFunc()
        return binFunc(x,y)
    return f

def foreach_in_row(A, I, func, reduceFunc=None, initial=0):
    N = A.shape[1]
    if reduceFunc:
        for k in xrange(N):
            initial = reduceFunc(initial, func(A[I, k]))
        return initial
    else:
        for k in xrange(N):
            func(A[I, k])

def foreach_in_col(A, I, func, reduceFunc=None, initial=0):
    N = A.shape[0]
    if reduceFunc:
        for k in xrange(N):
            if valid_numeric(A[I,k]) : initial = reduceFunc(initial, func(A[k, I]))
        return initial
    else:
        for k in xrange(N):
            if valid_numeric(A[I,k]) : func(A[k, I])

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
    nDim = 0
    d = foreach_pair_rows(A, I, J, square_diff, defPreBinaryFunc(lambda : nDim +=1, add), 0.0)
    return (d, nDim)

def cosine_distance(A, I, J):
    nDim = 0
    dot = foreach_pair_rows(A, I, J, lambda x, y: x*y, defPreBinaryFunc(lambda : nDim +=1, add), 0.0)
    if nDim > 0 :
        d1 = foreach_in_row(A, I, lambda x: x*x, add, 0.0)
        d2 = foreach_in_row(A, J, lambda x: x*x, add, 0.0)
        return (dot/d1*dot/d2, nDim)
    else:
        return (np.inf, nDim)


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

    return recommededMovie[u, m]: u, m are user & movie index. numpy.inf can be filled.
    """

    # todo scale rating to range [r0, r1], so that distance is not zero
    printMsg("Ratings:", ratings)

    #-- most popular movie index
    ratings_by_movie = [] # [ (movieIndex, rating) ]
    for i in xrange(NM):
        ratings_by_movie.push((i, foreach_in_col(ratings, i, lambda x:x, add, 0.0))

    ratings_by_movie = sorted(ratings_by_movie, key=itemgetter(i)

    printMsg("Most popular movie:", popularMi, midmap[popularMi])

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

    ru = np.full((userCount, MAX_RECOMM), np.inf)  # recommended MovieId
    for i in xrange(NU):
        wr = [] # [(movieIndex, rating)]: weighted rating for each movie
        for m in xrange(NM):
            if not valid_numeric(ratings[i, m]):  #  skip that user watched already.
                continue
            r = 0.0
            n = 0  # count valid ratings by similar users
            for j in xrange(NU):
                if valid_numeric(du[i,j]) and valid_numeric(rating[j, m]) :
                    r += rating[j, m] / du[i,j]
                    n += 1
            if n > 0: 
                wr.push((m, r))
        sortedMi = sorted(wr, key=itemgetter(1))  # sort by rating
        n = len(sortedMi)
        if n > MAX_RECOMM: n = MAX_RECOMM
        for k in range(n):
            ru[i, k] = sortedMi[k][0]
        # todo : if no recommended movies, select most populars or randomly pick up some
    return ru

#--- algo callback -----------------------------------------
def update_recommendation_by_review(record, mode):
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
        uid, mid = r.user.id, r.movie.movieId
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
            mi =NM
            midmap[mi] = mid
            midrmap[mid] = mi
            NM += 1
        ratings[ui, mi] = scaleRating(float(r.rating))


    #--- computing in different algorithms ------
    ru = jz_calculate_recommendations(ratings, userCount, movieCount, NU, NM)

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

if __filename__ == '__main__':
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movierecomm.settings")

    django.setup()
    update_recommendation_by_review(None, None)


