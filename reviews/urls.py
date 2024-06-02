from django.urls import path

from .views import review_kitchen, kitchen_comment_manage, manage_comment


app_name = 'review'


urlpatterns = [
    path('<int:kitchen_id>/', review_kitchen, name='kitchen'),
    path('kitchen-comment-manage/', kitchen_comment_manage, name='kitchen_comment_manage'),
    path('manage-comment/', manage_comment, name='manage_comment'),
]
