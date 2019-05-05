from django.db.models import Count
from django.shortcuts import render, get_object_or_404

from omr.forms import FileFilterForm
from omr.models import File, Author, Theme


def index(request):
    recent_files = File.objects.order_by('-added')[:5]

    context = {'title': 'Homepage', 'recent_files': recent_files}
    return render(request, 'omr/index.html', context)


def about(request):
    context = {'title': 'About'}
    return render(request, 'omr/about.html', context)


def statistics(request):
    total_files = File.objects.all().count()
    authors = Author.objects.annotate(num_files=Count('files')).order_by('-num_files')
    themes = Theme.objects.annotate(num_files=Count('sets__files')).order_by('-num_files')
    num_mainmodel = File.objects.filter(is_main_model=True).count()
    num_alternatemodel = File.objects.filter(is_main_model=False).count()

    context = {
        'title': 'Statistics',
        'total_files': total_files,
        'authors': authors,
        'themes': themes,
        'num_mainmodel': num_mainmodel,
        'num_alternatemodel': num_alternatemodel
    }
    return render(request, 'omr/statistics.html', context)


def file_list(request):
    files = File.objects.all()
    filter_form = FileFilterForm()

    context = {'title': 'All Files', 'files': files, 'filter_form': filter_form}
    return render(request, 'omr/file_list.html', context)


def file_detail(request, file_id):
    file = get_object_or_404(File, pk=file_id)

    context = {'title': file.model.set_num, 'file': file}
    return render(request, 'omr/file_detail.html', context)
