import json
from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .models import Wish, Wishlist


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


def index(request):
    wishlists = Wishlist.objects.all()
    context = {"wishlists": wishlists}
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
        print(image)
        print(request.POST)

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
        wish.delete()
        return JsonResponse({"success": True})
    except Wish.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item not found"}, status=404)