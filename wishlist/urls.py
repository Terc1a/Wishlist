from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    # path("logout/", views.logout, name="logout"),
    path("register/", views.register, name="register"),
    path("create_wishlist/", views.create_wishlist, name="create_wishlist"),
    path("create_wish/", views.create_wish, name="create_wish"),
    path("wishlist/<int:wishlist_id>/", views.wishlist_detail, name="wishlist_detail"),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),
]