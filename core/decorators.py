# core/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps
from .models import PerfilUsuario

def is_admin(user):
    """Verifica se o usuário é administrador"""
    if user.is_superuser or user.is_staff:
        return True
    
    try:
        perfil = PerfilUsuario.objects.get(usuario=user)
        return perfil.categoria == 'admin'
    except PerfilUsuario.DoesNotExist:
        return False

def is_admin_or_funcionario(user):
    """Verifica se o usuário é admin ou funcionário"""
    if user.is_superuser or user.is_staff:
        return True
    
    try:
        perfil = PerfilUsuario.objects.get(usuario=user)
        return perfil.categoria in ['admin', 'funcionario']
    except PerfilUsuario.DoesNotExist:
        return False

def admin_required(view_func):
    """Decorator que requer que o usuário seja admin"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if is_admin(request.user):
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return _wrapped_view

def admin_or_funcionario_required(view_func):
    """Decorator que requer que o usuário seja admin ou funcionário"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if is_admin_or_funcionario(request.user):
            return view_func(request, *args, **kwargs)
        return redirect('home')
    return _wrapped_view