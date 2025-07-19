from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create_wishlist/", views.create_wishlist, name="create_wishlist"),
    path("create_wish/", views.create_wish, name="create_wish"),
    path("wishlist/<int:wishlist_id>/", views.wishlist_detail, name="wishlist_detail"),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('set_like/<int:wishlist_id>/', views.set_like, name='like_wish'),
    path('profile/', views.profile, name='profile'),
    path('delete_wishlist/<int:wishlist_id>/', views.delete_wishlist, name='delete_wishlist'),
    path('update_item/<int:item_id>/', views.edit_wishlist_item, name='change_item'),
    path('update_wishlist/<int:wishlist_id>/', views.edit_wishlist, name='change_wishlist'),
    path('toggle_favorite/<int:item_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('search_users/', views.search_users, name='search_users')
]
