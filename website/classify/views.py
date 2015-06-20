from django.shortcuts import render
from .forms import UploadFileForm
from .libs.get_data_by_url import get_post_info


def classify_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_content = form.files['file'].read()
    else:
        file_content = ''
    return render(request, 'classify/chart.html', {'data': {'positive': 10, 'negative': 20, 'text': file_content}})


def classify_sentence(request):
    if request.method == 'POST':
        sentence = request.POST['sentence']

    return render(request, 'classify/chart.html', {'data': {'positive': 10, 'negative': 20, 'text': sentence}})


def classify_post(request):
    if request.method == 'POST':
        post_url = request.POST['post_url']
        data = {}

        with get_post_info() as x:
            data = x.get_post_data_from_url(post_url)

    return render(request, 'classify/chart.html', {'data': {'positive': 10, 'negative': 20, 'text':data}})
