from functools import wraps
from io import BytesIO
import base64

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import AtencionForm, PacienteEditForm, PacienteForm, UserEditForm, UserForm
from .models import Atencion, AuditoriaAtencion, Paciente, Perfil, User


ADMIN_PROFILE = 'I01'
ENCARGADO_PROFILE = 'I02'


def role_required(*profile_ids):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.is_superuser or request.user.perfil_id in profile_ids:
                return view(request, *args, **kwargs)
            raise PermissionDenied
        return wrapped
    return decorator


def home(request):
    return redirect('signin')


def signin(request):
    if request.user.is_authenticated:
        return redirect('panel-practicante' if request.user.perfil_id == ADMIN_PROFILE else 'panel-paciente')
    if request.method == 'GET':
        return render(request, 'signin.html')

    user = authenticate(
        request,
        username=request.POST.get('username', ''),
        password=request.POST.get('password', ''),
    )
    if user is None:
        return render(request, 'signin.html', {'error': 'Usuario o contrasena incorrecta.'})
    login(request, user)
    return redirect('panel-practicante' if user.perfil_id == ADMIN_PROFILE else 'panel-paciente')


@require_POST
@login_required
def signout(request):
    logout(request)
    return redirect('signin')


@role_required(ADMIN_PROFILE)
def panelPracticante(request):
    rows = User.objects.filter(perfil_id=ENCARGADO_PROFILE).order_by('rut')
    return render(request, 'pages/practicante/panel-practicante.html', {'rows': rows})


@require_POST
@role_required(ADMIN_PROFILE)
def searchPracticante(request):
    rows = User.objects.filter(pk=request.POST.get('rut', ''), perfil_id=ENCARGADO_PROFILE)
    return render(request, 'pages/practicante/panel-practicante.html', {'rows': rows})


@role_required(ADMIN_PROFILE)
def panelPracticanteAdd(request):
    if request.method == 'GET':
        return render(request, 'pages/practicante/panel-practicante-add.html')

    form = UserForm(request.POST)
    if form.is_valid():
        practicante = form.save(commit=False)
        practicante.perfil = get_object_or_404(Perfil, pk=ENCARGADO_PROFILE)
        practicante.save()
        return redirect('panel-practicante')
    return render(request, 'pages/practicante/panel-practicante-add.html', {'form': form})


@role_required(ADMIN_PROFILE)
def panelPracticanteEdit(request, rut):
    practicante = get_object_or_404(User, pk=rut, perfil_id=ENCARGADO_PROFILE)
    if request.method == 'GET':
        return render(request, 'pages/practicante/panel-practicante-edit.html', {'practicante': practicante})

    form = UserEditForm(request.POST, instance=practicante)
    if form.is_valid():
        updated = form.save(commit=False)
        updated.is_active = request.POST.get('is_active') == 'Activo'
        updated.save()
        return redirect('panel-practicante')
    return render(request, 'pages/practicante/panel-practicante-edit.html', {'practicante': practicante, 'form': form})


@require_POST
@role_required(ADMIN_PROFILE)
def panelPracticanteBloq(request, rut):
    practicante = get_object_or_404(User, pk=rut, perfil_id=ENCARGADO_PROFILE)
    practicante.is_active = False
    practicante.save(update_fields=['is_active'])
    return redirect('panel-practicante')


@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
def panelPaciente(request):
    rows = Paciente.objects.all().order_by('rut')
    return render(request, 'pages/paciente/panel-paciente.html', {'rows': rows})


@require_POST
@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
def searchPaciente(request):
    rows = Paciente.objects.filter(pk=request.POST.get('rut', ''))
    return render(request, 'pages/paciente/panel-paciente.html', {'rows': rows})


@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
def panelPacienteAdd(request):
    if request.method == 'GET':
        return render(request, 'pages/paciente/panel-paciente-add.html')
    form = PacienteForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect('panel-paciente')
    return render(request, 'pages/paciente/panel-paciente-add.html', {'form': form})


@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
def panelPacienteEdit(request, rut):
    paciente = get_object_or_404(Paciente, pk=rut)
    if request.method == 'GET':
        return render(request, 'pages/paciente/panel-paciente-edit.html', {'user': paciente})
    form = PacienteEditForm(request.POST, instance=paciente)
    if form.is_valid():
        updated = form.save(commit=False)
        updated.habilitado = request.POST.get('habilitado') == 'Activo'
        updated.save()
        return redirect('panel-paciente')
    return render(request, 'pages/paciente/panel-paciente-edit.html', {'user': paciente, 'form': form})


@require_POST
@role_required(ADMIN_PROFILE)
def panelPacienteBloq(request, rut):
    paciente = get_object_or_404(Paciente, pk=rut)
    paciente.habilitado = False
    paciente.save(update_fields=['habilitado'])
    return redirect('panel-paciente')


@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
def panelAtencion(request):
    rows = Atencion.objects.select_related('paciente', 'practicante').order_by('-fechaInicio')
    return render(request, 'pages/atencion/panel-atencion.html', _contexto_atenciones(request.user, rows))


@require_POST
@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
def searchAtencion(request):
    rows = Atencion.objects.filter(paciente_id=request.POST.get('rut', '')).select_related('paciente', 'practicante')
    return render(request, 'pages/atencion/panel-atencion.html', _contexto_atenciones(request.user, rows))


@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
@transaction.atomic
def panelAtencionAdd(request, rut):
    paciente = get_object_or_404(Paciente, pk=rut, habilitado=True)
    if request.method == 'GET':
        return render(request, 'pages/atencion/panel-atencion-add.html', {
            'paciente': paciente,
            'practicantes': _practicantes_permitidos(request.user),
        })

    form = AtencionForm(request.POST, user=request.user)
    if form.is_valid() and request.POST.get('terms'):
        atencion = form.save(commit=False)
        atencion.paciente = paciente
        atencion.terms = True
        if request.user.perfil_id == ENCARGADO_PROFILE and not request.user.is_superuser:
            atencion.practicante = request.user
        atencion.save()
        _registrar_auditoria(atencion, request.user, AuditoriaAtencion.CREACION, nuevos=_datos_atencion(atencion))
        return redirect('panel-atencion')
    if not request.POST.get('terms'):
        form.add_error(None, 'Debe confirmar que los datos fueron entregados por la persona.')
    return render(request, 'pages/atencion/panel-atencion-add.html', {
        'paciente': paciente,
        'practicantes': _practicantes_permitidos(request.user),
        'form': form,
    })


@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
@transaction.atomic
def panelAtencionEdit(request, id):
    atencion = get_object_or_404(Atencion, pk=id)
    if atencion.anulada:
        raise PermissionDenied
    if not _puede_editar_atencion(request.user, atencion):
        raise PermissionDenied
    if request.method == 'GET':
        return render(request, 'pages/atencion/panel-atencion-edit.html', {'atencion': atencion, 'practicantes': _practicantes_permitidos(request.user)})

    form = AtencionForm(request.POST, instance=atencion, user=request.user)
    if form.is_valid():
        valores_anteriores = _datos_atencion(atencion)
        hubo_cambios = form.has_changed()
        form.save()
        if hubo_cambios:
            _registrar_auditoria(
                atencion,
                request.user,
                AuditoriaAtencion.EDICION,
                anteriores=valores_anteriores,
                nuevos=_datos_atencion(atencion),
            )
        return redirect('panel-atencion')
    return render(request, 'pages/atencion/panel-atencion-edit.html', {'atencion': atencion, 'practicantes': _practicantes_permitidos(request.user), 'form': form})


@require_POST
@role_required(ADMIN_PROFILE)
@transaction.atomic
def panelAtencionAnular(request, id):
    atencion = get_object_or_404(Atencion, pk=id)
    motivo = request.POST.get('motivo_anulacion', '').strip()
    if atencion.anulada:
        return render(
            request,
            'pages/atencion/panel-atencion.html',
            _contexto_atenciones(request.user, Atencion.objects.select_related('paciente', 'practicante').order_by('-fechaInicio'), error='La atención ya fue anulada.'),
            status=400,
        )
    if not motivo:
        return render(
            request,
            'pages/atencion/panel-atencion.html',
            _contexto_atenciones(request.user, Atencion.objects.select_related('paciente', 'practicante').order_by('-fechaInicio'), error='Debe indicar el motivo de la anulación.'),
            status=400,
        )
    valores_anteriores = _datos_atencion(atencion)
    atencion.anulada = True
    atencion.fechaAnulacion = timezone.now()
    atencion.anuladoPor = request.user
    atencion.motivoAnulacion = motivo
    atencion.save(update_fields=['anulada', 'fechaAnulacion', 'anuladoPor', 'motivoAnulacion'])
    _registrar_auditoria(
        atencion,
        request.user,
        AuditoriaAtencion.ANULACION,
        motivo=motivo,
        anteriores=valores_anteriores,
        nuevos=_datos_atencion(atencion),
    )
    return redirect('panel-atencion')


@role_required(ADMIN_PROFILE, ENCARGADO_PROFILE)
def panelMetricas(request):
    return render(request, 'pages/metricas/panel-metricas.html', generar_metricas())


def _practicantes_permitidos(user):
    queryset = User.objects.filter(perfil_id=ENCARGADO_PROFILE, is_active=True)
    if user.perfil_id == ENCARGADO_PROFILE and not user.is_superuser:
        return queryset.filter(pk=user.pk)
    return queryset


def _es_administrador(user):
    return user.is_superuser or user.perfil_id == ADMIN_PROFILE


def _puede_editar_atencion(user, atencion):
    return _es_administrador(user) or atencion.practicante_id == user.pk


def _contexto_atenciones(user, rows, **extra):
    rows = list(rows)
    if _es_administrador(user):
        editable_atencion_ids = [row.id for row in rows if not row.anulada]
    else:
        editable_atencion_ids = [
            row.id for row in rows
            if not row.anulada and row.practicante_id == user.pk
        ]
    return {
        'rows': rows,
        'editable_atencion_ids': editable_atencion_ids,
        'puede_anular_atenciones': _es_administrador(user),
        **extra,
    }


def _datos_atencion(atencion):
    return {
        'sbp': atencion.sbp,
        'dbp': atencion.dbp,
        'pulso': atencion.pulso,
        'temperatura': atencion.temperatura,
        'saturacion': atencion.saturacion,
        'procedimiento': atencion.procedimiento,
        'razon_ingreso': atencion.razonIngreso,
        'practicante_id': atencion.practicante_id,
        'anulada': atencion.anulada,
        'fecha_anulacion': atencion.fechaAnulacion.isoformat() if atencion.fechaAnulacion else None,
        'anulado_por_id': atencion.anuladoPor_id,
        'motivo_anulacion': atencion.motivoAnulacion,
    }


def _registrar_auditoria(atencion, actor, accion, motivo='', anteriores=None, nuevos=None):
    AuditoriaAtencion.objects.create(
        atencion=atencion,
        actor=actor,
        accion=accion,
        motivo=motivo,
        valores_anteriores=anteriores or {},
        valores_nuevos=nuevos or {},
    )


def generar_metricas():
    por_motivo = Atencion.objects.filter(anulada=False).values('razonIngreso').annotate(cantidad=Count('id'))
    por_practicante = Atencion.objects.filter(anulada=False).values('practicante__nombre').annotate(cantidad=Count('id'))
    return {
        'img_motivo': _grafico_dona(por_motivo, 'razonIngreso', 'Motivo de Consulta'),
        'img_practicante': _grafico_dona(por_practicante, 'practicante__nombre', 'Practicantes'),
    }


def _grafico_dona(rows, label_key, title):
    rows = list(rows)
    fig, ax = plt.subplots(figsize=(8, 8))
    if not rows:
        ax.text(0.5, 0.5, 'Sin datos', ha='center', va='center', transform=ax.transAxes)
        ax.set_axis_off()
    else:
        labels = [row[label_key] for row in rows]
        values = [row['cantidad'] for row in rows]
        wedges, _, _ = ax.pie(values, autopct='%1.1f%%', startangle=90, pctdistance=0.8)
        ax.add_artist(plt.Circle((0, 0), 0.70, fc='white'))
        ax.legend(wedges, labels, title=title, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
    ax.set_title(title)
    image = BytesIO()
    fig.savefig(image, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(image.getvalue()).decode('utf-8')
