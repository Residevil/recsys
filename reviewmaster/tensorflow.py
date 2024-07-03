import numpy as np
import tensorflow as tf
import tensorflow_recommenders as tfrs
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model


class RecommenderModel(tfrs.Model):
    def __init__(self, num_biz, num_user):
        super().__init__()
        self.biz_embeddings = tf.keras.layers.Embedding(input_dim=num_biz, output_dim=5)
        self.user_embeddings = tf.keras.layers.Embedding(input_dim=num_user, output_dim=5)
        self.rating = tf.keras.layers.Dense(1)

    def call(self, inputs):
        user_embedding = self.user_embeddings(inputs['user_id'])
        biz_embedding = self.itemm_embeddings(inputs['biz_id'])
        return self.rating(tf.concat([user_embedding, biz_embedding], axis = 1))

    def compute_loss(self, features, training=False):
        user_embedding = self.user_embeddings(features['user_id'])
        biz_embedding = self.biz_embeddings(features['biz_id'])
        ratings_pred = self.rating(tf.concat([user_embedding, biz_embedding], axis=1))
        return tf.keras.losses.mean_squared_error(features['rating'], ratings_pred)

class Recommender(object):
    def __init__(self):
        self.num_user = ()
        self.num_biz = ()
        self.user_map = {}
        self.biz_map = {}

    def train(self):
        User = apps.get_model('reviewmaster', 'User')
        Business = apps.get_model('reviewmaster', 'Business')
        self.num_user = 1000
        self.num_biz = 1000
        user_ids = []
        biz_ids = []
        ratings= []
        self.user_map = {}
        self.biz_map = {}

        Review = apps.get_model('reviewmaster', 'Review')

        for review in Review.objects.all():
            if review.user_id not in self.user_map:
                self.user_map[review.user_id] = self.num_user
                self.num_user += 1
            user_ids.append(self.user_map[review.user_id])
            if review.business_id not in self.biz_map:
                self.biz_map[review.business_id] = self.num_biz
                self.num_biz += 1
            biz_ids.append(self.biz_map[review.business_id])
            ratings.append(review.rating)

        user_ids = np.array(user_ids)
        biz_ids = np.array(biz_ids)
        ratings = np.array(ratings)

        data = tf.data.Dataset.from_tensor_slices({
            "user_id": user_ids,
            "biz_id": biz_ids,
            "rating": ratings}).batch(2)
        # Train the model
        model = RecommenderModel(self.num_biz, self.num_user)
        model.compile(optimizer=tf.keras.optimizers.Adam(0.1))
        model.fit(data, epochs=100)
        model.save_weights(settings.TRAINED_MODEL_PATH)


    def recommend(self, user_id, model, limit=5):
        # Generate recommendations for a user
        User = apps.get_model('reviewmaster', 'User')
        Business = apps.get_model('reviewmaster', 'Business')

        user = User.objects.get(pk=user_id)
        all_biz_ids = Business.objects.values_list('pk', flat=True)

        # query = tf.constant([user_id])
        # candidates = tf.range(self.num_biz, dtype=tf.int32)
        user_embeddings = model.user_embeddings(np.array([self.user_map[user_id]]))
        biz_embeddings = model.biz_embeddings(np.array(list(self.biz_map.values())))

        # scores = tf.matmul(user_embeddings, biz_embeddings, transpose_b = True)
        # top_indices = tf.argsort(scores, axis=1, direction='DESCENDING')[0][:limit]
        # return top_indices.numpy()

        scores = tf.reduce_sum(tf.multiply(user_embeddings, biz_embeddings), axis=1).numpy()
        recommended_indices = scores.argsort()[-10:][::-1]

        recommended_biz_ids = [list(self.biz_map.keys())[index] for index in recommended_indices]
        return recommended_biz_ids