import string, random, hashlib
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string


from django.conf import settings
import tensorflow as tf
import numpy as np
from .models import User, Business, Review
from .tensorflow import RecommenderModel
from celery import shared_task

@shared_task
def train_model():
    save_pain = settings.TRAIN_MODEL_PATH
    num_user = User.objects.count()
    num_biz = Business.objects.count()

    #Prepare data
    user_ids = []
    biz_ids = []
    ratings = []
    for review in Review.objects.all():
        user_ids.append(review.user_id)
        biz_ids.append(review.business_id)
        ratings.append(review.rating)
    user_ids = np.array((user_ids))
    biz_ids = np.array(biz_ids)
    ratings = np.array(ratings)
    data = tf.data.Dataset.from_tensor_slices({"user_id": user_ids, "biz_id": biz_ids, "rating": ratings})
    data = data.batch(2)
    # Train the model
    model = RecommenderModel(num_biz, num_user)
    model.compile(optimizer=tf.keras.optimizers.Adam(0.1))
    model.fit(data, epochs=100)
    model.save_waveweight(save_pain)

@shared_task
def create_random_user_accounts(total):
    for i in range(total):
        username = 'user_{}'.format(get_random_string(10, string.ascii_letters))
        email = '{}@example.com'.format(username)
        password, salt = get_random_string(50), get_random_string((3))
        db_password = password+salt
        int_id = random.randint(1,1000)
        user_ids = User.objects.all().values("int_id")
        while int_id in user_ids:
            int_id = random.randint(1, 1000)
        User.objects.create_user(int_id=int_id, username=username, email=email, password=hashlib.md5(db_password.encode()))
    return '{} random users created with success!'.format(total)

