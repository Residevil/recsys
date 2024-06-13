import requests
from .models import User, Business, Review
from .forms import RegisterForm, LoginForm
from django import forms
from django.forms import ValidationError
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, ProcessFormView, FormView
from django.urls import reverse_lazy
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, UserCreationForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timesince, timezone
from django.utils.decorators import method_decorator

# Create your views here.

class IndexView(ListView):
     
    def get(self, request):
        return render(request, 'reviewmaster/index.html')

#@staff_member_required
# def user_index(request):
#     users = User.objects.all()
#     return render(request, 'reviewmaster/user_index.html', {'users': users})

# @staff_member_required
class UserIndexView(ListView):
    model = User
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["now"] =timezone.now()
    #     return context
    
    def get(self, request):
        users = User.objects.all()
        context = {'users': users}
        return render(request, 'reviewmaster/user_index.html', context)
        

# @login_required
# def user_detail(request, username):
    # user = get_object_or_404(User, pk=username)
    
    # rated_businesses = user.rated_businesses()
    # content_based_recommended_businesses = user.content_based_recommended_businesses()
    # collaborative_based_recommended_businesses = user.collaborative_based_Recommended_businesses()
    # if request.user != user:
    #     return redirect('business_index')
    # return render(request, 'reviewmaster/user_detail.html', {'user': user, 
    #                                                          'rated_businesses': rated_businesses,
    #                                                          'content_based_recommended_businesses': content_based_recommended_businesses,
    #                                                          'collaborative_based_recommended_businesses': collaborative_based_recommended_businesses})


class UserDetailView(DetailView):
    model = User
    context_object_name = 'user'
    
    # @login_required
    def get(self, request, username):
        user = get_object_or_404(User, pk=username)       
        rated_businesses = user.rated_businesses()
        content_based_recommended_businesses = user.content_based_recommended_businesses()
        collaborative_based_recommended_businesses = user.collaborative_based_Recommended_businesses()
        context = {'user': user, 
                    'rated_businesses': rated_businesses,
                    'content_based_recommended_businesses': content_based_recommended_businesses,
                    'collaborative_based_recommended_businesses': collaborative_based_recommended_businesses}
        if not request.user.is_authenticated:
            return HttpResponseRedirect(request, "login")
        # if request.user != user:
            # messages.error(request, "You are not the right user.")
            # return redirect('user_index')
        return render(request, 'reviewmaster/user_detail.html', context)
    
    def post(self, request, username):
        user = get_object_or_404(User, pk=username)       
        rated_businesses = user.rated_businesses()
        content_based_recommended_businesses = user.content_based_recommended_businesses()
        collaborative_based_recommended_businesses = user.collaborative_based_Recommended_businesses()
        context = {'user': user, 
                    'rated_businesses': rated_businesses,
                    'content_based_recommended_businesses': content_based_recommended_businesses,
                    'collaborative_based_recommended_businesses': collaborative_based_recommended_businesses}
        if request.user != user:
            return redirect('user_index')
        return render(request, 'reviewmaster/user_detail.html', context)

    def get_object(self):
        return self.request.user
    
    

# def business_index(request):
    # businesses = Business.objects.all()
    # return render(request, 'reviewmaster/business_index.html', {'businesses': businesses})
class BusinessIndexView(ListView):
    def get(self, request):
        businesses = Business.objects.all().order_by('name')
        context = {'businesses': businesses}
        return render(request, 'reviewmaster/business_index.html', context)
        
    def post(self, request):
        businesses = Business.objects.all().order_by('name')
        context = {'businesses': businesses}
        return render(request, 'reviewmaster/business_index.html', context)

# def business_detail(request, business_id):
#     business = get_object_or_404(Business, pk=business_id)
#     return render(request, 'reviewmaster/business_detail.html', {'business': business, 'id': business_id})

class BusinessDetailView(DetailView):
    def get(self, request, business_id):
        business = get_object_or_404(Business, pk=business_id)
        context = {'business': business}
        if request.business != business:
            return redirect('business_index')
        return render(request, 'reviewmaster/business_detail.html', context)
        
    def post(self, request, business_id):
        business = get_object_or_404(Business, pk=business_id)
        return render(request, 'reviewmaster/business_detail.html', {'business': business, 'id': business_id})

# def review_index(request):
#     reviews = Review.objects.all()
#     return render(request, 'reviewmaster/review_index.html', {'reviews': reviews})
    
class ReviewIndexView(ListView):
    def get(self, request):
        reviews = Review.objects.all().order_by('business')
        context = {"reviews": reviews}
        return render(request, 'reviewmaster/review_index.html', context)  
    
    def post(self, request):
        reviews = Review.objects.all().order_by('business')
        context = {"reviews": reviews}
        return render(request, 'reviewmaster/review_index.html', context) 
        


# def review_detail(request, review_id):
#     review = get_object_or_404(Review, pk=review_id)
#     return render(request, 'reviewmaster/review_detail.html', {'review': review, 'id': review_id})

class ReviewDetailView(DetailView):
    def get(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id)
        context = {'review': review, 'id': review_id}
        return render(request, 'reviewmaster/review_detail.html', context)
    
    def post(self, request, review_id):
        review = get_object_or_404(Review, pk=review_id)
        context = {'review': review, 'id': review_id}
        return render(request, 'reviewmaster/review_detail.html', context)

def demo_yelp_business(request):
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        'Authorization': 'Bearer ' + settings.YELP_API_KEY
    }
    params = {
        'location': 'Vancouver',
        'limit': 50
    }
    # Send the request to the Yelp Fusion API
    response = requests.get(url, headers=headers, params=params)
    return JsonResponse(response.json(), json_dumps_params={'indent': 4}, safe = False)


def demo_yelp_business_detail(request, business_id):
    url = f'https://api.yelp.com/v3/businesses/{business_id}'
    headers = {
        'accept': "application/json",
        'Authorization': 'Bearer ' + settings.YELP_API_KEY
    }
    params = {
        'limit': 10
    }
    # Send the request to the Yelp Fusion API
    response = requests.get(url, headers=headers, params=params)
    return JsonResponse(response.json(), json_dumps_params={'indent': 4}, safe = False)

def demo_yelp_business_reviews(request, business_id):
    url = f'https://api.yelp.com/v3/businesses/{business_id}/reviews'
    headers = {
        'accept': "application/json",
        'Authorization': 'Bearer ' + settings.YELP_API_KEY
    }
    params = {
        'limit': 10
    }
    # Send the request to the Yelp Fusion API
    response = requests.get(url, headers=headers, params=params)
    return JsonResponse(response.json(), json_dumps_params={'indent': 4}, safe = False)

def dump_yelp_data(request):
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {
        'Authorization': 'Bearer ' + settings.YELP_API_KEY
    }
    params = {
        'location': 'Vancouver',
        'limit': 50
    }
    business_count = 0
    review_count = 0
    actual_user_count = 0
    fake_user_count = 0
    # Send the request to the Yelp Fusion API
    response = requests.get(url, headers=headers, params=params)
    for business_data in response.json()['businesses']:
        # Create a new Business object and save it to the database
        business = Business(
            string_id = business_data['id'],
            alias = business_data['alias'],
            name = business_data['name'],
            image_url = business_data['image_url'],
            is_closed = business_data['is_closed'],
            url = business_data['url'],
            review_count = business_data['review_count'],
            rating = business_data['rating'],
            latitude = business_data['coordinates']['latitude'],
            longitude = business_data['coordinates']['longitude'],
            price = business_data.get('price', '$'),
            city = business_data['location']['city'],
            zip_code = business_data['location']['zip_code'],
            country = business_data['location']['country'],
            state = business_data['location']['state'],
            address = ''.join(business_data['location']['display_address']),
            phone = business_data['phone'],
        )
        business.save()
        business_count += 1
        
        # Make a separate API request to get the reviews for this business
        review_url = f'https://api.yelp.com/v3/businesses/{business_data["id"]}/reviews'
        review_params = {
            'limit': 10
        }
        review_response = requests.get(review_url, headers=headers, params=review_params)
        for review_data in review_response.json()['reviews']:
            # Update or create a user if not exist
            # (Considering the sparsity of user data, retain only the first alphanumeric characters of
            # the user id. In total, a max of 26*2 + 10 users will be saved)
            fake_id = review_data['user']['id'][0]
            fake_email = fake_id + '@example.com'
            user, created = User.objects.get_or_create(
                string_id = fake_id,
                defaults = {
                    'profile_url':  review_data['user']['profile_url'],
                    'image_url':    review_data['user']['image_url'],
                    'name':         review_data['user']['name'],
                    'email':        fake_email,
                    'username':     fake_id,
                },
            )
            actual_user_count += 1
            if created:
                fake_user_count += 1
            review = Review(
                string_id = review_data['id'],
                url = review_data['url'],
                text = review_data['text'],
                rating = review_data('rating'),
                time_created= review_data['time_created'],
                user = user,
                business = business,
            )
            review.save()
            review_count += 1
            
    return JsonResponse(
        data={
            'business_count': business_count,
            'review_count': review_count,
            'actual_user_count': actual_user_count,
            'fake_user_count': fake_user_count,
        }
    )


# class RegisterForm(UserCreationForm):
#     class Meta:
#         model = get_user_model() #models.User
#         field = ('email', 'username', 'password1', 'password2')
  
class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save(commit = False)
        user.username = user.username.lower()
        user.string_id = user.username
        user.save()
        messages.success(self.request, f'you have signed up successfully')
        if user:
            login(self.request, user)
            return redirect('index')
        else:
            return render(self.request, 'registration/register.html', {'form': form})
            
        # return super(RegisterView, self).form_valid(form)
    

class MyLoginView(LoginView):
    form_class = LoginForm
    template_name = "registration/login.html"

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password")
        return self.render_to_response(self.get_context_data(form=form))
        
    def post(self, request):
        form = self.form_class(request, request.POST) # type: ignore
        if form.is_valid():
            username=request.POST.get('username')
            password=request.POST.get('password')
            user = authenticate(request,
                                username = username,
                                password = password
                                )
            if user:
                messages.success(request,f'Hi {username}, welcome back!')
                login(request, user)
                return redirect('index')
            else: 
                messages.error(request, "invalid username or password")
        # self.form_invalid(form)
        else:
            messages.error(request, 'form is not valid')
            
            
        return render(request, self.template_name, {'form': form})
    

    

# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = \\\\authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect('user_detail', username=username)
#     else:
#         form = AuthenticationForm()
#     return render(request, 'registration/login.html', {'form': form})

class MyLogoutView(LogoutView):
    form_class = AuthenticationForm
    initial = {"key": "value"}
    template_name = "registration/logout.html"
    url = "/reviewmaster/templates/registration/logout.html"
    redirect_field_name = "login"
    next_page = reverse_lazy('login')
    
    def post(self, request):
        logout(request)
        messages.success(request, f'You have been logged out.')
        return redirect('login')
    
class PasswordChangeView(View):
    form_class = PasswordChangeForm
    initial = {"key": "value"}
    template_name = "password_change_form.html"
    url = "/reviewmaster/templates/registration/password_change.html"
    success_url = "/reviewmaster/templates/registration/password_change_done.html"
    redirect_field_name = "password_change_done"
    
    def get(self, request):
        form = self.form_class(initial=self.initial) # type: ignore
        return render(request, self.template_name, {"form": form}), 
    
    def post(self, request):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/success/")
        return render(request, self.template_name, {"form": form}),    
    

class PasswordChangeDoneView(View):
    form_class = PasswordResetForm
    initial = {"key": "value"}
    template_name = "password_change_done.html"
    success_url = "/reviewmaster/templates/registration/login.html"
    redirect_field_name = "login"
    
    def get(self, request):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {"form": form}), 
    
    def post(self, request):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/success/")
        return render(request, self.template_name, {"form": form})

class PasswordResetView(View):
    form_class = PasswordResetForm
    initial = {"key": "value"}
    template_name = "password_reset.html"
    url = "/reviewmaster/templates/registration/password_reset.html"
    success_url = "/reviewmaster/templates/registration/password_reset_done.html"
    redirect_field_name = "password_reset_done"
    
    def post(self, request):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            return HttpResponseRedirect("password_reset_done")
        return redirect('password_reset_done')
    
class PasswordResetDoneView(View):
    form_class = PasswordResetForm
    initial = {"key": "value"}
    template_name = "login.html"
    url = "/reviewmaster/templates/registration/password_reset_done.html"
    
    def post(self, request):
        form = self.form_class(request, request.POST)
        if form.is_valid():
            return HttpResponseRedirect("/login/")
        return redirect('login')    

@staff_member_required
class UserCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = User
    fields = ['string_id', 'profile_url', 'image_url', 'name']

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['string_id', 'profile_url', 'image_url', 'name']
    template_name_suffix = "_update_form"

class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("users")
    

class BusinessCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Business
    fields = ['string_id', 'alias', 'name', 'image_url', 
              'is_closed', 'review_count', 'rating', 
              'latitude', 'longitude', 'price', 
              'city', 'zip_code', 'country', 'state', 
              'address', 'phone', 'users']

class BusinessUpdateView(LoginRequiredMixin, UpdateView):
    model = Business
    fields = ['string_id', 'alias', 'name', 'image_url', 
              'is_closed', 'review_count', 'rating', 
              'latitude', 'longitude', 'price', 
              'city', 'zip_code', 'country', 'state', 
              'address', 'phone', 'users']    
    template_name_suffix = "_update_form"

class BusinessDeleteView(LoginRequiredMixin, DeleteView):
    model = Business
    success_url = reverse_lazy("businesses")


class ReviewCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'login'
    model = Review
    fields = ['string_id', 'url', 'text', 'rating', 'user', 'business', 'created_at', 'updated_at']

class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    fields = ['string_id', 'url', 'text', 'rating', 'user', 'business', 'created_at', 'updated_at']
    template_name_suffix = "_update_form"

class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    success_url = reverse_lazy("reviews")




# class PickyAuthenticationForm(AuthenticationForm):
#     def confirm_login_allowed(self, user):
#         if not user.is_active:
#             raise ValidationError(
#                 _("This account is inactive."),
#                 code="inactive",
#             )
