from django.test import TestCase

# Create your tests here.


class RecomendationTest(TestCase):
    def setup(self):
        pass

    def test_generate_recommendations(self):
        from .recommendation_algo import update_recommendation_by_review
        update_recommendation_by_review()
