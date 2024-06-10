import logging
from django.shortcuts import redirect, render
from menu.decorators import only_kitchen, only_manager
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from users.models import Kitchen
from table.models import Table
import zipfile
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files.storage import default_storage
import os


@only_manager
@only_kitchen
def index(request):
    page = request.GET.get("page" or None)
    user = request.user
    kitchen = user.kitchen
    all_tables = kitchen.tables.all().order_by('number')
    paginator = Paginator(all_tables, 10)
    try:
        tables = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tables = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results.
        tables = paginator.page(paginator.num_pages)
    if request.method == "POST":
        table_number = request.POST.get('table_number')
        print(table_number)
        try:
            table_numbers = int(table_number)
            if table_numbers > 10:
                messages.error(request, "Bir urinishda maksimal stollar soni 10 ta")
                return redirect("table:index")
            for i in range(1, table_numbers + 1):
                table = Table.objects.create(
                    kitchen=kitchen
                )
                table.save()
            messages.success(request, f'{table_numbers} tables created successfully')
            return redirect('table:index')
        except Exception as err:
            logging.error(err)
            return redirect('table:index')
    context = {
        "tables": tables
    }
    return render(request, 'kitchen/tables.html', context=context)


@only_kitchen
def delete_table(request):
    if request.method == "POST":
        table_count = request.POST.get('table_count')
        tables = request.user.kitchen.tables.all().order_by('-id')
        try:
            table_count = int(table_count)
            tables_to_delete = tables[:table_count]
            for table in tables_to_delete:
                table.delete()
            messages.success(request, f'{len(tables_to_delete)} ta stol o\'chirildi')
            return redirect('table:index')
        except Exception as err:
            logging.error(err)
            messages.error(request, 'Nimadir xato ketdi! Iltimos tekshirib qaytadan urinib ko\'ring')
            return redirect('table:index')


@only_kitchen
def edit_table(request):
    if request.method == "POST":
        table_id = request.POST.get('table-id')
        table_status = request.POST.get('table-status')
        table_name = request.POST.get('table_name')
        table = request.user.kitchen.tables.get(id=table_id)
        table.status = table_status
        if table_name:
            table.name = table_name
        table.save()
        messages.success(request, 'Table updated successfully')
        return redirect('table:index')
    messages.error(request, 'Get request is not allowed for this route')
    return redirect('table:index')



def download_qr_codes(request, kitchen_id):
    kitchen = get_object_or_404(Kitchen, pk=kitchen_id)
    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for table in Table.objects.filter(kitchen=kitchen):
            if table.qr_code:
                qr_code_path = os.path.join(settings.MEDIA_ROOT, table.qr_code.name)
                with default_storage.open(qr_code_path, 'rb') as qr_file:
                    qr_code_content = qr_file.read()
                qr_code_filename = f"kitchen_{kitchen.id}_table_{table.number}_qr.png"
                zip_file.writestr(qr_code_filename, qr_code_content)

    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename=kitchen_{kitchen.id}_qr_codes.zip'

    return response