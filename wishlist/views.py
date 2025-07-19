import json
from datetime import datetime

from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .models import Wish, Wishlist, WishLike


def login(request):
    """
    View to handle user login.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect("index")
        else:
            # Неверные данные — показать ошибку
            return render(request, "auth.html", {"error": "Неверный логин или пароль"})
    else:
        return render(request, "auth.html")


def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    wishlists = Wishlist.objects.all()
    context = {"wishlists": wishlists}
    print(request.user)
    return render(request, "index.html", context)

def register(request):
    pass


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


def wishlist_detail(request, wishlist_id):
    """
    View to display the details of a specific wishlist.
    """
    try:
        wishlist = Wishlist.objects.get(id=wishlist_id)
        wishes = Wish.objects.filter(wishlist=wishlist)
        print(wishes)
        context = {
            "wishlist": wishlist,
            "wishes": wishes,
        }
        return render(request, "wishlist_item.html", context)
    except Wishlist.DoesNotExist:
        return HttpResponse("Wishlist not found", status=404)

def delete_item(request, item_id):
    """
    View to delete a specific item from a wishlist.
    """
    try:
        wish = Wish.objects.get(id=item_id)
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
    context = {
        "user": user,
        "wishlists": wishlists,
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



#ToDo
# - Поиск профиля пользователя по логину
# - Избранные вишлисты и айтемы

