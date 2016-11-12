import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movierecomm.settings")

import django
django.setup()


if __name__ == '__main__':
    from reviews.recommendation_algo import update_recommendation_by_review
    update_recommendation_by_review(None, None)

