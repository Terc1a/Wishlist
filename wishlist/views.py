import json
from datetime import datetime

from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Count
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods

from .models import Wish, Wishlist, WishLike, WishFav


@require_http_methods(["GET", "POST"])
def login(request):
    """
    View to handle user login.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next", "/")

        if not username or not password:
            return JsonResponse({
                "success": False,
                "error": "Введите логин и пароль"
            }, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return JsonResponse({
                "success": True,
                "redirect": next_url
            })
        else:
            return JsonResponse({
                "success": False,
                "error": "Неверный логин или пароль"
            }, status=401)

    return render(request, "auth.html", {"next": request.GET.get("next", "/")})

def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    wishlists = Wishlist.objects.all()
    context = {"wishlists": wishlists}
    print(request.user)
    return render(request, "index.html", context)

def register(request):
    """
    View to handle user registration.
    """
    if request.method == "POST":
        username = request.POST.get("reg_username")
        email = request.POST.get("reg_email")
        password1 = request.POST.get("reg_password1")
        password2 = request.POST.get("reg_password2")

        # Проверяем валидность данных
        if not username or not email or not password1 or not password2:
            return JsonResponse({
                "success": False,
                "error": "Все поля должны быть заполнены"
            })

        if password1 != password2:
            return JsonResponse({
                "success": False,
                "error": "Пароли не совпадают"
            })

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                "success": False,
                "error": "Пользователь с таким именем уже существует"
            })

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                "success": False,
                "error": "Пользователь с таким email уже существует"
            })

        # Создаем нового пользователя
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1
            )
            auth_login(request, user)
            return JsonResponse({
                "success": True,
                "redirect": "/"
            })
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": "Ошибка при создании пользователя"
            })

    return render(request, "auth.html")


@login_required
def create_wishlist(request):
    """
    View to create a new wishlist.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        title = data["name"]
        description = data["description"]
        date = datetime.now()
        add_wish = Wishlist(title=title, description=description, created_at=date, user=request.user)
        add_wish.save()
        return JsonResponse({
            "success": True,
            "id": add_wish.id,  # пример, замените на реальный id
            "name": title,
            "description": description,
        })
    else:
        # Render the form
        return render(request, "create_wishlist.html")


@login_required
def create_wish(request):
    """
    View to create a new wish in a specific wishlist.
    """

    # надо переписать эту срань
    if request.method == "POST":
        wishlist_id = request.POST.get("wishlist_id")
        items = request.POST
        wishlist = Wishlist.objects.get(id=wishlist_id)
        image = request.FILES.get("item_image")  # Получаем файл
        date = datetime.now()

        add_wish = Wish(
            item_name=items["item_name"],
            item_description=items["item_desc"],
            item_url=items["item_link"],
            item_price=float(items["item_price"]),
            item_image= image,  # Handle optional image
            created_at=date,
            wishlist=wishlist,
        )
        add_wish.save()

        return JsonResponse({'success': True})
    else:
        return render(request, "index.html")


@login_required
def wishlist_detail(request, wishlist_id):
    """
    View to display the details of a specific wishlist.
    """
    try:
        wishlist = Wishlist.objects.get(id=wishlist_id)
        # Получаем список желаний с количеством избранных и статусом избранного для текущего пользователя
        wishes = Wish.objects.filter(wishlist=wishlist).annotate(
            favorites_count=Count('wishfav')
        )

        if request.user.is_authenticated:
            # Добавляем информацию о том, добавил ли текущий пользователь предмет в избранное
            for wish in wishes:
                wish.is_favorite = WishFav.objects.filter(
                    wish=wish,
                    user=request.user
                ).exists()

        return render(request, "wishlist_item.html", {
            "wishlist": wishlist,
            "wishes": wishes
        })
    except Wishlist.DoesNotExist:
        return HttpResponse("Wishlist not found", status=404)

@login_required
def delete_item(request, item_id):
    """
    View to delete a specific item from a wishlist.
    """
    try:
        wish = Wish.objects.get(id=item_id)
        # Проверяем, что текущий пользователь является владельцем вишлиста
        if wish.wishlist.user != request.user:
            return JsonResponse({"success": False, "error": "Недостаточно прав"}, status=403)

        wishlist = wish.wishlist
        wishes_count = Wish.objects.filter(wishlist=wishlist).count()
        if wishes_count <=1:
            delete_wishlist = Wishlist.objects.get(id=wish.wishlist.id)
            delete_wishlist.delete()
            wish.delete()
            return JsonResponse({"success": True})
        else:
            wish.delete()
            return JsonResponse({"success": True})
    except Wish.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item not found"}, status=404)


@login_required
def set_like(request, wishlist_id):
    """
    View to like a wish in a specific wishlist.
    """
    if request.method == "POST":
        try:
            wishlist = Wishlist.objects.get(id=wishlist_id)
            print(wishlist.id)
            like, created = WishLike.objects.get_or_create(user=request.user, wishlist=wishlist)
            if created:
                wishlist.likes += 1
                wishlist.save()
                return JsonResponse({"success": True, "likes": wishlist.likes})
            else:
                like.delete()
                wishlist.likes -= 1
                wishlist.save()
                return JsonResponse({"success": True, "likes": wishlist.likes})
        except (Wishlist.DoesNotExist, Wish.DoesNotExist):
            return JsonResponse({"success": False, "error": "Wishlist or wish not found"}, status=404)
    else:
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


@login_required
def profile(request):
    """
    View to display the user's profile.
    """
    user = request.user
    wishlists = Wishlist.objects.filter(user=user)
    wishfavs = WishFav.objects.filter(user=user)
    context = {
        "user": user,
        "wishlists": wishlists,
        "favorite_items": wishfavs
    }
    return render(request, "profile.html", context)


@login_required
def delete_wishlist(request, wishlist_id):
    """
    View to delete a specific wishlist.
    """
    try:
        wishlist = Wishlist.objects.get(id=wishlist_id, user=request.user)
        wishlist.delete()
        return JsonResponse({"success": True})
    except Wishlist.DoesNotExist:
        return JsonResponse({"success": False, "error": "Wishlist not found"}, status=404)


@login_required
def edit_wishlist_item(request, item_id):
    """
    View to edit a specific wishlist item
    """
    try:
        item = Wish.objects.get(id=item_id)
        item.item_name= request.POST.get("item_name")
        item.item_description = request.POST.get("item_description")
        item.item_url = request.POST.get("item_url")
        item.item_price = float(request.POST.get("item_price"))
        if "item_image" in request.FILES:
            item.item_image = request.FILES["item_image"]  # Handle optional image
        item.save()
        return JsonResponse({"success": True})
    except Wish.DoesNotExist:
        return JsonResponse({"success": False, "error": "Wishlist not found"}, status=404)


@login_required
def edit_wishlist(request, wishlist_id):
    """
    View to edit a specific wishlist
    """
    try:
        wishlist = Wishlist.objects.get(id=wishlist_id, user=request.user)
        wishlist.title = request.POST.get("name")
        wishlist.description = request.POST.get("description")
        wishlist.save()
        return JsonResponse({"success": True})
    except Wishlist.DoesNotExist:
        return JsonResponse({"success": False, "error": "Wishlist not found"}, status=404)


@login_required
def toggle_favorite(request, item_id):
    """
    Toggle favorite status for a wish item
    """
    try:
        wish = Wish.objects.get(id=item_id)
        wish_fav, created = WishFav.objects.get_or_create(
            wish=wish,
            user=request.user
        )

        if not created:
            # Если запись уже существовала, удаляем её (убираем из избранного)
            wish_fav.delete()

        return JsonResponse({
            'success': True,
            'is_favorite': created
        })
    except Wish.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Предмет не найден'
        })


def search_users(request):
    query = request.GET.get('query', '')  # получаем параметр поиска из формы
    if query:
        # Поиск пользователей с аннотацией количества вишлистов
        users = User.objects.filter(
            username__icontains=query
        ).annotate(
            wishlists_count=Count('wishlist')
        )
    else:
        users = []

    context = {
        "found_users": users,
        "query": query
    }
    return render(request, "search_results.html", context)


def handler404(request, exception=None):
    return render(request, 'error.html', {
        'error_code': 404,
        'error_title': 'Страница не найдена',
        'error_message': 'К сожалению, запрашиваемая страница не существует.'
    }, status=404)

def handler500(request, *args, **argv):
    return render(request, 'error.html', {
        'error_code': 500,
        'error_title': 'Ошибка сервера',
        'error_message': 'Произошла внутренняя ошибка сервера. Попробуйте позже.'
    }, status=500)

def handler403(request, exception=None):
    return render(request, 'error.html', {
        'error_code': 403,
        'error_title': 'Доступ запрещен',
        'error_message': 'У вас нет прав для доступа к этой странице.'
    }, status=403)
