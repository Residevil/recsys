from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import tensorflow as tf

from django.conf import settings
from .tensorflow import RecommenderModel, Recommender
from .managers import CustomUserManager

# Create your models here.

class User(AbstractUser):
    int_id = models.IntegerField(primary_key=True, unique=True)
    profile_url = models.URLField(max_length=1000, null=True)
    image_url = models.URLField(max_length=1000, null=True)

    email = models.EmailField(_("email address"), unique=True)
    # age = models.IntegerField()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    def rated_businesses(self):
        return self.business_set.all()
    
    def content_based_recommended_businesses(self):
        # Get all businesses the user has rated
        rated_businesses = self.review_set.all().values_list('business', flat = True)
        
        # Get the cities of the rated businesses
        rated_businesses_cities = Business.objects.filter(pk__in=rated_businesses).values_list('city', flat=True)
        
        # Get all businesses in the same cities as the rated businesses
        recommended_businesses = Business.objects.filter(city__in=rated_businesses_cities).exclude(pk__in=rated_businesses)
        
        return recommended_businesses

    def collaborative_based_Recommended_businesses(self):
        # Get all reviews by the current user
        user_reviews = self.review_set.all()
        
        # Create a dictionary of business IDs and their corresponding ratings
        rated_businesses_ratings = {review.business: review.rating for review in user_reviews}
        
        # Find similar users who have rated the same businesses with the same ratings
        similar_users = User.objects.exclude(pk=self.pk).filter(
            review__business__in=rated_businesses_ratings.keys()
        ).annotate(
            matching_ratings_count=models.Count('review', filter=models.Q(review__rating__in=rated_businesses_ratings.values()))
        ).filter(
            matching_ratings_count=len(rated_businesses_ratings)
        ).distinct()
        
        # Get all businesses similar users have rated
        similar_businesses = Business.objects.filter(
            review__user__in=similar_users,
            review__rating__gte=4
        )
        
        # Get the businesses that the current user has not rated
        recommended_businesses = similar_businesses.exclude(
            review__business__in=rated_businesses_ratings.keys()
        ).distinct()
                
        return recommended_businesses

    def tensorflow_recommended_businesses(self, limit=5):
        # recommender = Recommender()
        # recommender.train()
        # user_id = self.pk
        # recommended_biz_ids = recommender.recommend(user_id)
        # recommended_businesses = Business.objects.filter(pk__in=recommended_biz_ids)
        # return recommended_businesses
        recommender = Recommender()
        recommender.train()
        model = RecommenderModel(1000, 1000)
        model.load_weights(settings.TRAINED_MODEL_PATH)
        query = tf.constant([self.int_id])
        candidates = tf.range(1000, dtype=tf.int32)
        user_embeddings = model.user_embeddings(query)
        biz_embeddings = model.biz_embeddings(candidates)
        scores = tf.matmul(user_embeddings, biz_embeddings, transpose_b=True)
        top_indices = tf.argsort(scores, axis=1, direction='DESCENDING')[0][:limit]
        return Business.objects.filter(int_id__in=top_indices.numpy())

    # def tensorflow_recommended_businesses_with_city(self, limit=5):
    #     model = RecommenderModel(Business.objects.count(), User.objects.count())
    #     model.load_weights(settings.TRAINED_MODEL_PATH)
    #     query = tf.constant([self.int_id])
    #     candidates = tf.range(Business.objects.count(), dtype=tf.int32)
    #     user_embeddings = model.user_embeddings(query)
    #     biz_embeddings = model.biz_embeddings(candidates)
    #     scores = tf.matmul(user_embeddings, biz_embeddings, transpose_b=True)
    #     top_indices = tf.argsort(scores, axis=1, direction='DESCENDING')[0][:limit]
    #     return Business.objects.filter(id__in=top_indices.numpy()).filter()


    def __str__(self):
        return self.email
    
class Business(models.Model):
    PRICE = {
        ('$',   'Cheap'),
        ('$$',  'Reasonable'),
        ('$$$', 'Expensive'),
        ('$$$$','Luxurious'),
    }
    int_id = models.IntegerField(primary_key=True, unique=True)
    alias = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    image_url = models.URLField(max_length=1000, null=True)
    url = models.URLField(max_length=1000)
    is_closed = models.BooleanField()
    review_count = models.PositiveIntegerField()
    rating = models.FloatField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    price = models.CharField(
        max_length=10,
        choices=PRICE,
    )
    city = models.CharField(max_length=200, default=None)
    zip_code = models.CharField(max_length=20, default=None)
    country = models.CharField(max_length=200, default=None)
    state = models.CharField(max_length=200, default=None)
    address = models.CharField(max_length=200, default=None)
    phone = models.CharField(max_length=20, default=None)
    users = models.ManyToManyField(to=User, blank=True, through='Review')
    
    class Meta:
        ordering = ["-name"]
    
    def average_rating(self):
        # Get the average of all rating for the business
        review = Review.objects.filter(business = self).aggregate(average=avg('rating'))
        avg = 0
        

    def __str__(self):
        return str(self.name) + " at " + str(self.city)

class Review(models.Model):
    RATING_STARS = [
        (1, 'One Star'),
        (2, 'Two Star'),
        (3, 'Three Star'),
        (4, 'Four Star'),
        (5, 'Five Star'),
    ]
    int_id = models.IntegerField(primary_key=True, unique=True)
    url = models.URLField(max_length=1000)
    text = models.TextField()
    rating = models.IntegerField(choices=RATING_STARS)
    user = models.ForeignKey(User, models.CASCADE)
    business = models.ForeignKey(Business, models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-business']

    def __str__(self):
        return str(self.user.username)\
            + " rates " + str(self.business)\
            + " with a " + str(self.rating)\
            + " Star at "\
            + str(self.created_at)