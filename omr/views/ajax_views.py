from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.shortcuts import render

from omr.models import File


def file_table(request):
    files = File.objects.all()

    themes = request.GET.get('themes')
    if themes:
        files = files.filter(model__theme__in=parameter_split(themes))

    authors = request.GET.get('authors')
    if authors:
        files = files.filter(author__in=parameter_split(authors))

    is_main_model = request.GET.get('is_main_model')
    if is_main_model:
        files = files.filter(is_main_model=is_main_model)

    missing_parts = request.GET.get('missing_parts')
    if missing_parts:
        files = files.filter(missing_parts=missing_parts)

    missing_patterns = request.GET.get('missing_patterns')
    if missing_patterns:
        files = files.filter(missing_patterns=missing_patterns)

    missing_stickers = request.GET.get('missing_stickers')
    if missing_stickers:
        files = files.filter(missing_stickers=missing_stickers)

    search = request.GET.get('search')
    if search:
        files = files.filter(Q(model__set_num__icontains=search) | Q(model__name__icontains=search))

    # Sort Order
    sort_order = request.GET.get('so', None)

    if sort_order == 'snum':
        # Default model ordering is by set number, so we don't have to do anything here,
        # just making sure the code doesn't execute the else
        pass
    elif sort_order == 'sname':
        files = files.order_by('model__name')
    elif sort_order == 'stheme':
        files = files.order_by('model__theme')
    elif sort_order == 'author':
        files = files.order_by('author')
    elif sort_order == 'added-asc':
        files = files.order_by('added')
    elif sort_order == 'added-desc':
        files = files.order_by('-added')
    else:
        pass

    # Display Type
    display_type = request.GET.get('dt', None)

    if display_type == 'table':
        num_items = 100
        template = 'table'
    elif display_type == 'list':
        num_items = 30
        template = 'list'
    else:
        num_items = 100
        template = 'table'

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(files, num_items)

    try:
        files = paginator.page(page)
    except PageNotAnInteger:
        files = paginator.page(1)
    except EmptyPage:
        files = paginator.page(paginator.num_pages)

    context = {'files': files}
    return render(request, f'omr/includes/file_{template}.html', context)


def parameter_split(parameter):
    if ',' in parameter:
        output = list(filter(bool, parameter.split(',')))
        if output[0].isdigit():
            output = [int(x) for x in output]
    else:
        # The parameter is already a single value, but we make it a list nonetheless so that this method
        # always retuns a list
        if parameter.isdigit():
            output = [int(parameter)]
        else:
            output = [parameter]
    return output
