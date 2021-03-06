import logging

from django.urls import reverse, reverse_lazy
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse, HttpResponseRedirect

from django.db.models import Q
from django.template.defaultfilters import slugify

from django.views.generic.base import View
from django.views.generic import (
    ListView, FormView, DetailView, 
    FormView,TemplateView, CreateView, 
    UpdateView, DeleteView
)

from .forms import AuthRegisterForm
from django.contrib.auth.models import User
from .models import Perfil, Publicacao, Comentario

class HomePageView(ListView):
    model = Publicacao
    template_name = 'blog/index.html'
    ordering = ['created']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            name_format = f"{request.user.first_name.upper() }"
            name_format += request.user.last_name.upper()

            obj, created = Perfil.objects.get_or_create(
                user=self.request.user,
                    defaults={
                        'user':request.user,
                        'name':(
                            name_format if len(name_format) > 1 else request.user.username.upper()
                        )
                    }
                )
        else:
            return HttpResponseRedirect(reverse_lazy('blog:login'))

        return super(
            HomePageView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        perfil = None

        try:
            perfil = self.request.user.perfil
        except AttributeError:
            pass

        if perfil:
            return queryset.filter(
                Q(author__perfil__in=perfil.seguidores.all()) &
                ~Q(author=perfil.user)
            ).order_by('-created').distinct()

        return Publicacao.objects.none()


class AuthRegisterView(FormView):
    form_class = AuthRegisterForm
    template_name = 'registration/register.html'
    sucess_url = 'blog:login'

    def form_valid(self, form):
        if self.request.method == "POST":
            form = AuthRegisterForm(self.request.POST)
            if form.is_valid():
                form.save()
        else:
            form = AuthRegisterForm()

        return super(
            AuthRegisterView, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.sucess_url)


class PublicacaoDetailView(DetailView):
    model = Publicacao
    template_name = 'blog/publicacao_detail.html'

    def get_context_data(self, **kwargs):
        kwargs.update({
            'comentarios':Comentario.objects.filter(
                publicacao= self.get_object()
            )
        })

        return super().get_context_data(**kwargs)



class PerfilView(DetailView):
    model = Perfil
    slug_field = "user__username"
    template_name = "blog/profile.html"

    def get_context_data(self, **kwargs):
        posts = Publicacao.objects.filter(
            author=self.get_object().user
        ).order_by('-created')

        kwargs.update({
            'posts':posts
        })

        return super(PerfilView, self).get_context_data(**kwargs)


