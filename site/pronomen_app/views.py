from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.conf import settings


def index(request):
    return render(request, 'pronomen_app/index.html', {'pronouns': settings.PRONOUNS})


def detail(request, pronoun_id):
    return render(request, 'pronomen_app/detail.html', {'pronoun': settings.PRONOUNS[pronoun_id]})

