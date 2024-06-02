import logging
from django.shortcuts import redirect, render, get_object_or_404
from menu.decorators import only_kitchen
from users.models import Kitchen, User
from .models import ReviewKitchen
from django.contrib import messages


def review_kitchen(request, kitchen_id):
    kitchen = get_object_or_404(Kitchen, id=kitchen_id)
    comments = ReviewKitchen.objects.filter(kitchen=kitchen).order_by("-created")
    if request.method == "POST":
        if request.user.is_authenticated:
            text = request.POST.get("post_body")
            user = request.user
            if not text:
                messages.warning(request, "Bo'sh xabarlar qabul qilinmaydi!")
                return redirect("review:kitchen", kitchen.id)

            try:
                comment = ReviewKitchen.objects.create(
                    kitchen=kitchen,
                    user=user,
                    body=text
                )
                comment.save()
                messages.success(request, "Sharh yuborildi!")
            except Exception as err:
                logging.error(err)
                messages.error(request, "Nimadir xato ketdi!...")
            return redirect("review:kitchen", kitchen.id)
    context = {
        "comments": comments,
        "kitchen": kitchen,
    }
    return render(request, "main/review_kitchen.html", context=context)


def manage_comment(request):
    if request.method == "POST":
        comment_id = request.POST.get("comment_id" or None)
        action = request.POST.get("action" or None)
        comment = get_object_or_404(ReviewKitchen, id=comment_id)
        if action == "delete":
            comment.delete()
            messages.success(request, "Sharh o'chirildi!")
        elif action =="reply":
            text = request.POST.get("replyText")
            user = request.user
            try:
                reply = ReviewKitchen.objects.create(
                    kitchen=comment.kitchen,
                    user=user,
                    body=text,
                    reply_to=comment
                )
                reply.save()
                messages.success(request, "Sharh yuborildi!")
            except Exception as err:
                logging.error(err)
                messages.error(request, "Nimadir xato ketdi!...")
        return redirect("review:kitchen", comment.kitchen.id)


@only_kitchen
def kitchen_comment_manage(request):
    comments = ReviewKitchen.objects.filter(kitchen=request.user.kitchen).order_by("-created")
    if request.method == "POST":
        comment_id = request.POST.get("comment_id" or None)
        action = request.POST.get("action" or None)
        comment = get_object_or_404(ReviewKitchen, id=comment_id)
        if action == "delete":
            comment.delete()
            messages.success(request, "Sharh o'chirildi!")
        elif action =="reply":
            text = request.POST.get("replyText")
            user = request.user
            try:
                reply = ReviewKitchen.objects.create(
                    kitchen=request.user.kitchen,
                    user=user,
                    body=text,
                    reply_to=comment
                )
                reply.save()
                messages.success(request, "Javob yuborildi!")
            except Exception as err:
                logging.error(err)
                messages.error(request, "Nimadir xato ketdi!...")
        return redirect("review:kitchen_comment_manage")
    context = {
        "comments": comments,
    }
    return render(request, "kitchen/kitchen_comment_manage.html", context=context)