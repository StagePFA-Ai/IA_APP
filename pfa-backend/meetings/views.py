from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from .models import  Reunion, Audio, Transcription, Resume, Rapport
from .forms import LoginForm, ReunionForm, AudioUploadForm
from django.contrib.auth.forms import AuthenticationForm
import json
from django.urls import reverse, NoReverseMatch
from django.db.models import Count
from django.db.models.functions import TruncMonth
import datetime
# meetings/views_meeting.py
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from .models import Reunion
from django.utils.dateparse import parse_date
from datetime import date,time
from django.urls import reverse
import re
from django.conf import settings as dj_settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import date, datetime, time as dtime
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.core.paginator import Paginator
# la premier page 
def home(request):
    # page publique : pas besoin d'auth
    return render(request, "HTML/home.html")

# Login view
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            login(request, user)
            return redirect(request.GET.get("next") or "dashboard")
        messages.error(request, "Identifiants incorrects")
    return render(request, "HTML/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
# Dashboard view
def _month_add(d: date, months: int) -> date:
    y = d.year + ((d.month - 1 + months) // 12)
    m = (d.month - 1 + months) % 12 + 1
    return date(y, m, 1)

@login_required
def dashboard(request):
    
    user = request.user
    today = timezone.localdate()

    meetings_qs = Reunion.objects.filter(utilisateur=user)

    total_meetings = meetings_qs.count()

    total_seconds = (
        Audio.objects.filter(reunion__utilisateur=user)
        .aggregate(s=Sum("duree"))
        .get("s") or 0
    )
    heures = round(total_seconds / 3600, 1)

    resumes_count = Resume.objects.filter(
        transcription__reunion__utilisateur=user
    ).count()

    # ⚠️ Valeurs de status : adapte à TES choices exacts.
    # Si ton modèle a 'planifier' (et pas 'planifie'), mets 'planifier'.
    actions = meetings_qs.filter(
        status__in=["planifie", "en_cours"],  # ou ["planifier","en_cours"]
        date_r__gte=today
    ).count()

    kpis = {
        "total_meetings": total_meetings,
        "heures": heures,
        "Résumés": resumes_count,
        "actions": actions,
    }

    meetings_by_month = (
        Reunion.objects
        .annotate(month=TruncMonth('date_r'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    chart1_labels = [m['month'].strftime("%b %Y") for m in meetings_by_month]
    chart1_data = [m['count'] for m in meetings_by_month]
    recent_meetings = list(
        meetings_qs.order_by("-date_r", "-heure_r")[:8]
    )
    ctx = {
        "kpis": kpis,
        "chart1_labels": chart1_labels,
        "chart1_data": chart1_data,
         "recent_meetings": recent_meetings
    }
    return render(request, "HTML/dashboard.html", ctx)
# Calendar view
# meetings/views_calendar.py
from datetime import date as ddate, time as dtime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date


from .models import Reunion  # adapte si le modèle est ailleurs

User = get_user_model()

# --------- Constantes ---------
STATUS_LABELS = {
    "planifie": "Planifié",
    "en_cours":  "En cours",
    "termine":  "Terminé",
    "annule":   "Annulé",
    "reporte":  "Reporté",
}

STATUS_COLORS = {
    "planifie": "#2563eb",  # bleu
    "en_cours":  "#10b981",  # vert
    "termine":  "#6b7280",  # gris
    "annule":   "#ef4444",  # rouge
    "reporte":  "#f59e0b",  # orange
}

# --------- Helpers ---------
def _today_local():
    return timezone.localdate()

def _parse_hhmm(s: str):
    """'HH:MM' -> datetime.time | None"""
    try:
        h, m = (s or "").split(":")
        return dtime(int(h), int(m))
    except Exception:
        return None

def _scope_user(user):
    """Réunions visibles par l'utilisateur : créateur OU participant."""
    return Q(utilisateur=user) | Q(participants=user)

def _can_start(m: Reunion) -> bool:
    """Démarrage autorisé uniquement le jour J si statut 'planifier'."""
    return m.status == "planifier" and m.date_r == _today_local()

def _can_resume(m: Reunion) -> bool:
    """Rejoindre la transcription si réunion en cours le jour J."""
    return m.status == "en_cours" and m.date_r == _today_local()

def _can_edit(m: Reunion, user: User) -> bool: # type: ignore
    """Le créateur peut modifier :
       - si réunion aujourd'hui ou future
       - si reportée (pour replanifier)"""
    if m.utilisateur_id != user.id:
        return False
    if m.status == "reporter":
        return True
    return m.date_r >= _today_local()

def _autopostpone_overdue(user: User): # type: ignore
    """Marque 'reporter' les réunions du user dépassées restées 'planifier'."""
    today = _today_local()
    Reunion.objects.filter(utilisateur=user, status="planifier", date_r__lt=today).update(status="reporter")

# --------- Vues Calendrier ---------
@login_required
def calendar(request):
    """Page calendrier (colonne droite préremplie avec aujourd’hui)."""
    selected_date = parse_date(request.GET.get("date") or "") or _today_local()

    meetings_on_date = (
        Reunion.objects
        .filter(_scope_user(request.user), date_r=selected_date)
        .select_related("utilisateur")
        .prefetch_related("participants")
        .order_by("heure_r", "titre")
        .distinct()
    )

    # auto-report “planifier” passées
    _autopostpone_overdue(request.user)

    return render(request, "HTML/calendar.html", {
        "selected_date": selected_date,
        "meetings_on_date": meetings_on_date,
    })

@login_required
def calendar_events(request):
    """Événements pour FullCalendar (toutes réunions visibles)."""
    qs = (
        Reunion.objects
        .filter(_scope_user(request.user))
        .select_related("utilisateur")
        .distinct()
    )
    events = []
    for r in qs:
        events.append({
            "id": r.id,
            "title": r.titre,
            "start": f"{r.date_r.isoformat()}T{r.heure_r.strftime('%H:%M')}",
            "url": reverse("view_meeting", args=[r.id]),
            "color": STATUS_COLORS.get(r.status, "#2563eb"),
        })
    return JsonResponse(events, safe=False)

@login_required
def calendar_day(request):
    """Réunions d’un jour (pour remplir la colonne de droite)."""
    try:
        day_str = request.GET.get("date", "")
        d = parse_date(day_str) or _today_local()
    except Exception:
        return HttpResponseBadRequest("date invalide")

    _autopostpone_overdue(request.user)

    qs = (
        Reunion.objects
        .filter(_scope_user(request.user), date_r=d)
        .select_related("utilisateur")
        .prefetch_related("participants")
        .order_by("heure_r", "titre")
        .distinct()
    )

    payload = {
        "date": d.isoformat(),
        "meetings": []
    }
    for m in qs:
        can_start  = _can_start(m)
        can_resume = _can_resume(m)

        if can_resume:
            hint = "Réunion en cours — vous pouvez la rejoindre."
        elif m.status == "reporter":
            hint = "Réunion dépassée non démarrée : replanifie-la."
        elif not can_start and m.date_r == _today_local():
            hint = "Le démarrage n’est possible que si le statut est ‘Planifié’."
        elif not can_start and m.date_r != _today_local():
            hint = "Le démarrage est autorisé uniquement le jour J."
        else:
            hint = ""

        payload["meetings"].append({
            "id": m.id,
            "titre": m.titre,
            "date": m.date_r.isoformat(),
            "heure": m.heure_r.strftime("%H:%M"),
            "status": m.status,
            "status_label": STATUS_LABELS.get(m.status, m.status),
            "can_start": can_start,
            "can_resume": can_resume,
            "resume_url": reverse("transcription", args=[m.id]) if can_resume else "",
            "hint": hint,
        })
    return JsonResponse(payload)

@login_required
def calendar_create(request):
    """Créer une réunion (modale ‘Nouvelle réunion’)."""
    if request.method != "POST":
        return HttpResponseBadRequest("Méthode non supportée")

    titre = (request.POST.get("titre") or "").strip()
    d = parse_date(request.POST.get("date") or "")
    t = _parse_hhmm(request.POST.get("heure") or "")

    if not titre or not d or not t:
        return JsonResponse({"ok": False, "error": "Champs manquants"}, status=400)

    r = Reunion.objects.create(
        titre=titre,
        date_r=d,
        heure_r=t,
        status="planifier",
        utilisateur=request.user,
    )
    return JsonResponse({"ok": True, "id": r.id})

@login_required
def calendar_meeting_info(request, pk: int):
    """Infos pour la modale 'Gérer' (droits + démarrer/rejoindre)."""
    try:
        m = (Reunion.objects
             .select_related("utilisateur")
             .prefetch_related("participants")
             .get(Q(pk=pk) & _scope_user(request.user)))
    except Reunion.DoesNotExist:
        return HttpResponseBadRequest("Réunion introuvable ou non autorisée")

    # Auto-report si planifiée & dépassée
    if m.status == "planifier" and m.date_r < _today_local():
        m.status = "reporter"
        m.save(update_fields=["status"])

    can_start  = _can_start(m)
    can_resume = _can_resume(m)
    can_edit   = _can_edit(m, request.user)

    # Participants (tous les users affichés — adapte si besoin)
    selected_ids = set(m.participants.values_list("id", flat=True))
    participants_all = []
    for u in User.objects.order_by("username").values("id", "username", "first_name", "last_name"):
        label = (f"{u['first_name']} {u['last_name']}".strip()) or u["username"]
        participants_all.append({
            "id": u["id"],
            "label": label,
            "selected": u["id"] in selected_ids,
        })

    if can_resume:
        hint = "Réunion en cours — vous pouvez la rejoindre."
    elif m.status == "reporter":
        hint = "Cette réunion a été reportée car elle a dépassé sa date sans démarrage. Replanifie-la."
    elif m.date_r == _today_local() and not can_start:
        hint = "Le démarrage n’est possible que si le statut est ‘Planifié’."
    elif m.date_r != _today_local() and not can_start:
        hint = "Le démarrage est autorisé uniquement le jour J."
    else:
        hint = ""

    data = {
        "id": m.id,
        "titre": m.titre,
        "date": m.date_r.isoformat(),
        "heure": m.heure_r.strftime("%H:%M"),
        "status": m.status,
        "status_label": STATUS_LABELS.get(m.status, m.status),
        "can_start": can_start,
        "can_edit": can_edit,
        "can_resume": can_resume,
        "resume_url": reverse("transcription", args=[m.id]) if can_resume else "",
        "participants_all": participants_all,
        "hint": hint,
    }
    return JsonResponse(data)

@login_required
def calendar_meeting_update(request):
    """Met à jour date/heure/participants (créateur uniquement)."""
    if request.method != "POST":
        return HttpResponseBadRequest("Méthode invalide")

    pk = request.POST.get("id")
    try:
        m = Reunion.objects.select_related("utilisateur").get(pk=pk)
    except Reunion.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Réunion introuvable"}, status=400)

    if not _can_edit(m, request.user):
        return JsonResponse({"ok": False, "error": "Modification non autorisée"}, status=403)

    # maj date/heure
    d = parse_date(request.POST.get("date") or "")
    t = _parse_hhmm(request.POST.get("heure") or "")
    if not d or not t:
        return JsonResponse({"ok": False, "error": "Date/heure invalides"}, status=400)
    m.date_r, m.heure_r = d, t

    # participants
    ids = request.POST.getlist("participants")
    if ids:
        m.participants.set(User.objects.filter(id__in=ids))
    else:
        m.participants.clear()

    # si 'reporter' et replanifiée aujourd’hui/futur → redevient planifiée
    if m.status == "reporter" and m.date_r >= _today_local():
        m.status = "planifier"

    m.save()
    return JsonResponse({"ok": True})

@login_required
def calendar_start(request):
    """Démarrage d’une réunion (jour J & statut planifié)."""
    if request.method != "POST":
        return HttpResponseBadRequest("Méthode invalide")

    pk = request.POST.get("id")
    try:
        m = Reunion.objects.select_related("utilisateur").get(pk=pk)
    except Reunion.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Réunion introuvable"}, status=400)

    if not _can_start(m):
        return JsonResponse({"ok": False, "error": "Le démarrage est autorisé uniquement le jour J pour une réunion planifiée."}, status=403)

    if m.status != "en_cours":
        m.status = "en_cours"
        m.save(update_fields=["status"])

    return JsonResponse({"ok": True, "redirect": reverse("transcription", args=[m.id])})

# --------- (Optionnel) Détail réunion, utilisé par les liens "Voir" ---------
@login_required
def view_meeting(request, meeting_id: int):
    m = get_object_or_404(Reunion.objects.select_related("utilisateur"), id=meeting_id)
    is_owner = (m.utilisateur_id == request.user.id)
    is_participant = m.participants.filter(id=request.user.id).exists()
    if not (is_owner or is_participant or request.user.is_superuser):
        return HttpResponseForbidden("Accès interdit.")

    audios = m.audios.all().order_by("-id")
    total_seconds = audios.aggregate(s=Sum("duree")).get("s") or 0
    total_hours = round(total_seconds / 3600, 2)

    transcription = getattr(m, "transcription", None)
    resume = getattr(transcription, "resume", None) if transcription else None
    rapport = getattr(resume, "rapport", None) if resume else None

    return render(request, "HTML/meeting_detail.html", {
        "meeting": m,
        "is_owner": is_owner,
        "participants": m.participants.all(),
        "audios": audios,
        "total_audio_seconds": total_seconds,
        "total_audio_hours": total_hours,
        "transcription": transcription,
        "resume": resume,
        "rapport": rapport,
    })

#view reunions 

@login_required
def meetings_page(request):
    """
    Liste des réunions de l'utilisateur (créées par lui ou où il est participant),
    avec recherche plein texte (titre, transcription, résumé), filtres statut / dates,
    et pagination.
    """
    user = request.user

    # Base : réunions où l’utilisateur est créateur OU participant
    qs = (Reunion.objects
          .filter(Q(utilisateur=user) | Q(participants=user))
          .distinct())

    # --- Filtres GET ---
    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()       # planifier, en_cours, terminer, annuler, reporter
    dfrom = parse_date(request.GET.get("date_from") or "")
    dto   = parse_date(request.GET.get("date_to") or "")

    if q:
        qs = qs.filter(
            Q(titre__icontains=q) |
            Q(transcription__text_transcrit__icontains=q) |
            Q(transcription__resume__text_resume__icontains=q)
        )

    if status in {"planifier","en_cours","terminer","annuler","reporter"}:
        qs = qs.filter(status=status)

    if dfrom:
        qs = qs.filter(date_r__gte=dfrom)
    if dto:
        qs = qs.filter(date_r__lte=dto)

    # Tri récent d'abord
    qs = (qs.select_related("utilisateur",
                            "transcription",
                            "transcription__resume")  # pour accès direct au résumé
            .prefetch_related("participants", "audios")     # pour boucler sans requêtes N+1
            .order_by("-date_r", "-heure_r", "-id"))

    # Pagination
    paginator = Paginator(qs, 8)  # 8 cartes par page
    page_obj = paginator.get_page(request.GET.get("page"))

    ctx = {
        "meetings": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
        "status": status,
        "date_from": dfrom.isoformat() if dfrom else "",
        "date_to": dto.isoformat() if dto else "",
    }
    return render(request, "HTML/meetings.html", ctx)
#view seeting
@login_required
def settings_page(request):
    """
    Paramètres en SESSION (aucun changement de models).
    Clés session:
      user_settings = {
        auto_record: bool,
        recording_consent: bool,     # autoriser enregistrement audio local
        disable_reunions: bool,      # désactiver tout le module Réunions/Calendrier
        doc_notes: str,
      }
    """
    sess = request.session.setdefault("user_settings", {})

    if request.method == "POST":
        def asbool(v): return str(v).lower() in {"1", "true", "on", "yes", "oui"}
        sess["auto_record"]       = asbool(request.POST.get("auto_record"))
        sess["recording_consent"] = asbool(request.POST.get("recording_consent"))
        

        request.session["user_settings"] = sess
        request.session.modified = True
        messages.success(request, "Paramètres enregistrés.")
        return redirect("settings")

    ctx = {
        "settings": {
            "auto_record":       bool(sess.get("auto_record", False)),
            "recording_consent": bool(sess.get("recording_consent", True)),
           
        },
        "user_info": request.user,
        # Texte affiché
        "app_description": (
            "MeetingAI est une application locale (on-premise) qui transcrit les réunions "
            "avec Whisper / faster-whisper et génère des résumés multilingues (FR/EN/AR). "
            "Toutes les données restent dans l’infrastructure de l’entreprise."
        ),
        "arch_points": [
            "Frontend Django + Bootstrap (Dashboard, Réunions, Calendrier, Paramètres).",
            "Capture micro navigateur (WebRTC) → backend ASGI.",
            "Transcodage en PCM 16 kHz mono → Transcription (Whisper/faster-whisper).",
            "Résumé multilingue (mT5/LLM) côté backend.",
            "Persistance : Audio, Transcription, Résumé, Rapport (suivant permissions).",
        ],
        # Chemins purement informatifs (lecture seule)
        "media_root": dj_settings.MEDIA_ROOT,
        "audio_upload_path": "uploads/audio/",
        "reports_upload_path": "uploads/rapports/",
        "files_upload_path": "uploads/",
    }
    return render(request, "HTML/settings.html", ctx)
# nouvelle reunion view
def reunion_form(request, reunion_id=None):
    """
    Affiche le formulaire :
      - création si reunion_id est None
      - modification sinon
    Contexte attendu par le template : reunion, utilisateurs
    """
    reunion = None
    if reunion_id:
        reunion = get_object_or_404(Reunion, pk=reunion_id)
        # sécurité : seul le créateur peut modifier
        if reunion.utilisateur != request.user:
            messages.error(request, "Vous n'êtes pas autorisé à modifier cette réunion.")
            return redirect("meetings")

    # liste des utilisateurs proposés comme participants
    utilisateurs = User.objects.all().order_by("username")

    return render(
        request,
        "HTML/nouvelle_reunion.html",
        {"reunion": reunion, "utilisateurs": utilisateurs},
    )

from django.db import IntegrityError, transaction
@login_required
def creer_reunion(request):
    if request.method == "POST":
        titre = (request.POST.get("titre") or "").strip()
        date_str = request.POST.get("date_r")
        heure_str = request.POST.get("heure_r")
        action = request.POST.get("action")  # "enregistrer" ou "demarrer"

        # validation basique
        if not titre or not date_str or not heure_str:
            messages.error(request, "Veuillez renseigner le titre, la date et l’heure.")
            return redirect("creer_reunion")  # ou renvoyer le formulaire

        try:
            date_r = datetime.strptime(date_str, "%Y-%m-%d").date()
            heure_r = datetime.strptime(heure_str, "%H:%M").time()
        except ValueError:
            messages.error(request, "Format de date/heure invalide.")
            return redirect("creer_reunion")

        # 1) Prévenir le doublon avant insert
        conflict = Reunion.objects.filter(
            utilisateur=request.user,
            date_r=date_r,
            heure_r=heure_r,
            titre=titre,
        ).exists()
        if conflict:
            messages.error(
                request,
                "Une réunion avec ce titre, cette date et cette heure existe déjà pour votre compte."
            )
            return redirect("creer_reunion")

        # 2) Création + ceinture et bretelles avec try/except
        try:
            with transaction.atomic():
                reunion = Reunion.objects.create(
                    titre=titre,
                    date_r=date_r,
                    heure_r=heure_r,
                    utilisateur=request.user,
                    # status par défaut = 'planifier' selon ton modèle
                )

                # participants (liste d'IDs)
                p_ids = request.POST.getlist("participants")
                if p_ids:
                    reunion.participants.set(User.objects.filter(id__in=p_ids))

                # action : démarrer = passer en cours et rediriger vers transcription
                if action == "demarrer":
                    reunion.status = "en_cours"
                    reunion.save(update_fields=["status"])
                    messages.success(request, "Réunion démarrée.")
                    return redirect("transcription", reunion_id=reunion.id)

            messages.success(request, "Réunion enregistrée.")
            # Choisis où retourner (page réunions, calendrier, dashboard…)
            return redirect("meetings")

        except IntegrityError:
            # Si malgré le .exists() on a un conflit (course), on gère proprement
            messages.error(
                request,
                "Conflit détecté : une réunion identique vient d’être créée. Réessayez avec un autre horaire ou un autre titre."
            )
            return redirect("creer_reunion")

    # GET : afficher le formulaire de création
    utilisateurs = User.objects.exclude(id=request.user.id).order_by("username")
    return render(request, "HTML/nouvelle_reunion.html", {"utilisateurs": utilisateurs})


@login_required
def modifier_reunion(request, reunion_id):
    """
    Traite le POST de modification depuis le formulaire.
    Actions possibles :
      - modifier : met à jour les champs
      - demarrer : met 'en_cours' et envoie vers transcription
    """
    reunion = get_object_or_404(Reunion, pk=reunion_id)
    if reunion.utilisateur != request.user:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette réunion.")
        return redirect("meetings")

    if request.method != "POST":
        # si quelqu’un tente GET directement sur cette route, on renvoie le formulaire
        return redirect("reunion_modifier", reunion_id=reunion.id)

    titre = (request.POST.get("titre") or "").strip()
    date_r = request.POST.get("date_r")
    heure_r = request.POST.get("heure_r")
    action = request.POST.get("action")  # 'modifier' ou 'demarrer'

    if not titre or not date_r or not heure_r:
        messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        return redirect("reunion_modifier", reunion_id=reunion.id)

    # mise à jour
    reunion.titre = titre
    reunion.date_r = date_r
    reunion.heure_r = heure_r

    # participants
    participants_ids = request.POST.getlist("participants")
    reunion.participants.set(User.objects.filter(id__in=participants_ids))

    # action
    if action == "demarrer":
        reunion.status = "en_cours"
    else:
        # si on ne démarre pas explicitement, on laisse le statut tel quel
        # (optionnel) si tu veux rebasculer en "planifier" lors d'une maj future :
        # reunion.status = "planifier"
        pass

    reunion.save()

    if action == "demarrer":
        messages.success(request, "Réunion démarrée.")
        try:
            return redirect("transcription", reunion_id=reunion.id)
        except Exception:
            return redirect(f"/transcription/?reunion_id={reunion.id}")

    messages.success(request, "Réunion mise à jour.")
    return redirect("meetings")

def reunion_nouvelle(request):
    return reunion_form(request, reunion_id=None)


# view transcription
# meetings/views.py

from django.views.decorators.http import require_POST


@login_required
def transcription_page(request, reunion_id: int):
    reunion = get_object_or_404(Reunion, pk=reunion_id, utilisateur=request.user)

    # objets existants (facultatif pour pré-remplir)
    transcription = getattr(reunion, "transcription", None)
    resume = getattr(transcription, "resume", None) if transcription else None

    ctx = {
        "reunion": reunion,
        "transcription": transcription,
        "resume": resume,
        "webrtc_ws_url": "/ws/transcription/",  # utilisé par ton template
    }
    return render(request, "HTML/transcription.html", ctx)


@login_required
def save_transcription(request, reunion_id: int):
    if request.method != "POST":
        return HttpResponseForbidden("Méthode non autorisée")
    reunion = get_object_or_404(Reunion, pk=reunion_id, utilisateur=request.user)

    text = (request.POST.get("text") or "").strip()
    summary = (request.POST.get("summary") or "").strip()
    lang = (request.POST.get("lang") or "fr").strip()

    if not text:
        return JsonResponse({"ok": False, "error": "Texte vide"}, status=400)

    # upsert Transcription
    tr, _created = Transcription.objects.get_or_create(
        reunion=reunion,
        defaults={"text_transcrit": text, "langue": lang, "heure_date": timezone.now()},
    )
    if not _created:
        tr.text_transcrit = text
        tr.langue = lang
        tr.heure_date = timezone.now()
        tr.save()

    # upsert Resume (si summary fourni)
    if summary:
        rs, _c2 = Resume.objects.get_or_create(
            transcription=tr, defaults={"text_resume": summary}
        )
        if not _c2:
            rs.text_resume = summary
            rs.save()

    # si tu veux marquer la réunion comme "terminée" après sauvegarde
    if reunion.status != "terminer":
        reunion.status = "terminer"
        reunion.save(update_fields=["status"])

    return JsonResponse({"ok": True, "transcription_id": tr.id})
from docx import Document
from docx.shared import Pt, Inches
from tempfile import NamedTemporaryFile
import os

# ------- Rapport (DOCX) -------
# meetings/views.py
import os
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import FileResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from docx import Document
from docx.shared import Inches

from .models import Reunion, Transcription, Resume, Rapport
from django.contrib.auth import get_user_model

User = get_user_model()

def _can_view(reunion, user):
    return (
        reunion.utilisateur_id == user.id
        or reunion.participants.filter(id=user.id).exists()
        or user.is_superuser
    )
@login_required
def meeting_report_view(request, pk):
    r = get_object_or_404(Reunion.objects.select_related("utilisateur"), pk=pk)
    if not _can_view(r, request.user):
        return HttpResponseForbidden("Accès refusé.")

    transcription = getattr(r, "transcription", None)
    resume = getattr(transcription, "resume", None) if transcription else None
    audios = r.audios.all() if hasattr(r, "audios") else []
    total_seconds = sum(getattr(a, "duree", 0) for a in audios)
    total_hours = round(total_seconds / 3600, 2)

    # Si tu as un modèle Decision, remplace par ta vraie requête
    decisions = getattr(r, "decisions", None)

    ctx = {
        "reunion": r,
        "participants": r.participants.all(),
        "transcription": transcription,
        "resume": resume,
        "decisions": decisions,
        "audios": audios,
        "total_audio_hours": total_hours,
        "now": timezone.now(),
        "generate_url": reverse("generate_report", args=[r.id]),
    }
    return render(request, "HTML/meeting_report.html", ctx)
@login_required
def generate_report(request, reunion_id: int):
    """
    Génère un DOCX avec infos réunion + résumé + transcription.
    Nécessite: pip install python-docx
    """
    r = get_object_or_404(Reunion.objects.select_related("utilisateur"), pk=reunion_id)

    if not _can_view(r, request.user):
        return HttpResponseForbidden("Accès refusé.")

    tr = getattr(r, "transcription", None)
    if not tr or not (tr.text_transcrit or "").strip():
        messages.error(request, "Aucune transcription enregistrée pour cette réunion.")
        return redirect("transcription", r.id)  # adapte le nom d'URL si besoin

    rs = getattr(tr, "resume", None)
    if not rs:
        # ⚠️ Important: créer le résumé AVANT de créer le rapport
        rs = Resume.objects.create(
            transcription=tr,
            text_resume="(Résumé non fourni — à compléter)",
            langue=getattr(tr, "langue", "fr") or "fr",
        )

    # ------- DOCX -------
    doc = Document()
    doc.add_heading("Rapport de réunion", level=1)

    # Logo optionnel
    logo_path = os.path.join(getattr(settings, "MEDIA_ROOT", ""), "logo.png")
    if os.path.exists(logo_path):
        try:
            doc.add_picture(logo_path, width=Inches(1.2))
        except Exception:
            pass

    # Métadonnées
    doc.add_paragraph(f"Titre : {r.titre}")
    doc.add_paragraph(f"Date : {r.date_r.strftime('%d/%m/%Y')} à {r.heure_r.strftime('%H:%M')}")
    doc.add_paragraph(f"Statut : {r.get_status_display()}")

    # Participants
    if r.participants.exists():
        doc.add_heading("Participants", level=2)
        for u in r.participants.all():
            doc.add_paragraph(u.get_full_name() or u.username, style="List Bullet")

    # Résumé
    doc.add_heading("Résumé", level=2)
    doc.add_paragraph(rs.text_resume or "(non disponible)")

    # Décisions (si tu as un modèle et des données)
    decisions = getattr(r, "decisions", None)
    if decisions:
        doc.add_heading("Décisions", level=2)
        # adapte selon ta structure
        for d in decisions.all() if hasattr(decisions, "all") else decisions:
            doc.add_paragraph(f"• {getattr(d, 'titre', str(d))}", style="List Bullet")

    # Transcription
    doc.add_heading("Transcription", level=2)
    doc.add_paragraph(tr.text_transcrit)

    # ------- Sauvegarde et attachement -------
    with NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        doc.save(tmp.name)
        tmp.flush()
        tmp_path = tmp.name

    # Attache au Rapport (OneToOne avec Resume)
    rapport, _ = Rapport.objects.get_or_create(resume=rs)
    filename = f"rapport_reunion_{r.id}_{timezone.now().strftime('%Y%m%d_%H%M')}.docx"
    with open(tmp_path, "rb") as f:
        rapport.fichier.save(filename, File(f), save=True)

    os.remove(tmp_path)

    # Téléchargement direct
    return FileResponse(rapport.fichier.open("rb"), as_attachment=True, filename=filename)
