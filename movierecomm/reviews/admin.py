from django.contrib import admin

# Register your models here.

from .models import Movie, Review, RecommendedMovieList

class DynamicLookupMixin(object):
    '''
    a mixin to add dynamic callable attributes like 'book__author' which
    return a function that return the instance.book.author value
    '''

    def __getattr__(self, attr):
        if ('__' in attr
            and not attr.startswith('_')
            and not attr.endswith('_boolean')
            and not attr.endswith('_short_description')):

            def dyn_lookup(instance):
                # traverse all __ lookups
                return reduce(lambda parent, child: getattr(parent, child),
                              attr.split('__'),
                              instance)

            # get admin_order_field, boolean and short_description
            dyn_lookup.admin_order_field = attr
            dyn_lookup.boolean = getattr(self, '{}_boolean'.format(attr), False)
            dyn_lookup.short_description = getattr(
                self, '{}_short_description'.format(attr),
                attr.replace('_', ' ').capitalize())

            return dyn_lookup

        # not dynamic lookup, default behaviour
        return self.__getattribute__(attr)


class ReviewAdmin(admin.ModelAdmin, DynamicLookupMixin):
    model = Review
    list_display = ('movie__title', 'rating', 'user__username', 'comment', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['user__username']

#    def username(me):
#        return me.user.username
#    user__name.admin_order_field  = "user__name"
#    user__name.short_description = "User Name"

#    def movietitle(me):
#        return me.movie.title
#    movie__title.admin_order_field  = "movie__title"
#    movie__title.short_description = "Movie title"

class MovieAdmin(admin.ModelAdmin, DynamicLookupMixin):
    model = Movie
    list_display = ('title', 'genres')
    list_filter = ['genres']
    search_fields = ['title']

class RecommendedMovieListAdmin(admin.ModelAdmin, DynamicLookupMixin):
    model = Movie
    list_display = ('algo', 'user__username', 'priority',  'movie__title')
    list_filter = ['algo']
    search_fields = ['user__username, movie__title']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(RecommendedMovieList, RecommendedMovieListAdmin)

