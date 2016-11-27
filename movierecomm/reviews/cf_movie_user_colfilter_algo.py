
import pandas as pd
import numpy as np
from operator import itemgetter

def isZero(v):
    return abs(v) < 1.0e-6

def predict_topk(ratings, similarity, k=15):
    pred = np.zeros(ratings.shape)
    for i in xrange(ratings.shape[0]):
        top_k_users = [np.argsort(similarity[:,i])[:-k-1:-1]]
        for j in xrange(ratings.shape[1]):
            pred[i,j] = similarity[i,:][top_k_users].dot(ratings[:,j][top_k_users])
            pred[i,j] /= np.sum(np.abs(similarity[i,:][top_k_users]))
            
    return pred

def recommend_all(user_ratings,score_matrix, n=10):  
    print "user_ratings.shape:", user_ratings.shape, "score_matrix.shape:", score_matrix.shape
    Nusers = user_ratings.shape[0]
    Nitems = user_ratings.shape[1]
    user_recom = {}   # {userIndex: [ (itemIndex, itemScore) ]
    for user in xrange(Nusers):
        recom_items = []  #  [ (itemIndex, itemScore) ]
        for i in xrange(Nitems):
            rating = user_ratings[user, i]
            if isZero(rating):
                recom_items.append( (i, score_matrix[user, i]) )
        sorted_items = sorted(recom_items, key=itemgetter(1), reverse=True )
        user_recom[user] = sorted_items[:n] 

    return user_recom

def cf_similar_users_recommendations(ratings, userCount, movieCount, NU, NM, MAX_RECOMM=5):
    """ ratings[u, m]: movie i rating by user u
    userCount, movieCount: number of users and movies
    Nu, NM : valid number of users and movies. all the reset are set numpy.nan

    return recommededMovies: { userIndex: [(movieIndex, priority) ] } .
    """
    from sklearn.metrics.pairwise import pairwise_distances
    UI = np.nan_to_num(ratings)[:userCount, :movieCount]
    user_similarity = pairwise_distances(UI, metric='cosine')
    user_prediction = predict_topk(UI, user_similarity)
    return recommend_all(UI, user_prediction)
