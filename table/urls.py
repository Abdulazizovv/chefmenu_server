from django.urls import path
from .views import (
    index,
    delete_table,
    edit_table,
    download_qr_codes,
    )


app_name = 'table'

urlpatterns = [
    path('', index, name='index'),
    path('delete/', delete_table, name='delete'),
    path('edit/', edit_table, name='edit'),
    path('download_qr_codes/<int:kitchen_id>/', download_qr_codes, name='download_qr_codes'),
]
