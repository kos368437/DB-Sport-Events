from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from django.urls import path
from .views import MainView, EventDetailView, SignUpView, SignInView

urlpatterns = [
    path('', MainView.as_view(), name='index'),
    path('events/<slug>/', EventDetailView.as_view(), name='event_detail'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('signout/', LogoutView.as_view(), {'next_page': settings.LOGOUT_REDIRECT_URL}, name='signout',),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
