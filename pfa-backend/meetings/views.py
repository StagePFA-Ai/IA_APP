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
def _scope_user(user):
    """Renvoie un filtre Q pour les réunions visibles par l'utilisateur."""
    return Q(utilisateur=user) | Q(participants=user)

def _parse_hhmm(s: str):
    """'HH:MM' -> datetime.time"""
    try:
        h, m = (s or "").split(":")
        return dtime(int(h), int(m))
    except Exception:
        return None

STATUS_COLORS = {
    "planifier": "#2563eb",  # bleu
    "en_cours": "#10b981",   # vert
    "terminer": "#6b7280",   # gris
    "annuler": "#ef4444",    # rouge
    "reporter": "#f59e0b",   # orange
}

def _user_label(u: User) -> str:
    full = f"{u.first_name} {u.last_name}".strip()
    return full or u.username

# ------------------------
# Page Calendrier
# ------------------------

@login_required
def calendar(request):
    """Rendu serveur de la page calendrier avec la colonne du jour préremplie (aujourd’hui par défaut)."""
    selected_date = parse_date(request.GET.get("date") or "") or timezone.localdate()

    meetings_on_date = (
        Reunion.objects
        .filter(_scope_user(request.user), date_r=selected_date)
        .select_related("utilisateur")
        .prefetch_related("participants")
        .order_by("heure_r", "titre")
        .distinct()
    )

    ctx = {
        "selected_date": selected_date,
        "meetings_on_date": meetings_on_date,
    }
    return render(request, "HTML/calendar.html", ctx)

# ------------------------
# JSON: events pour FullCalendar
# ------------------------

@login_required
def calendar_events(request):
    """Renvoie la liste des événements pour FullCalendar (toutes les réunions visibles)."""
    qs = (
        Reunion.objects
        .filter(_scope_user(request.user))
        .select_related("utilisateur")
        .distinct()
    )

    events = []
    for r in qs:
        start = f"{r.date_r.isoformat()}T{r.heure_r.strftime('%H:%M')}"
        events.append({
            "id": r.id,
            "title": r.titre,
            "start": start,
            "url": reverse("view_meeting", args=[r.id]),  # adapte le nom si besoin
            "color": STATUS_COLORS.get(r.status, "#2563eb"),
        })
    return JsonResponse(events, safe=False)

# ------------------------
# JSON: réunions d’un jour
# ------------------------

@login_required
def calendar_day(request):
    """Renvoie les réunions d’un jour (GET ?date=YYYY-MM-DD) pour remplir la colonne de droite."""
    d = parse_date(request.GET.get("date") or "") or timezone.localdate()
    qs = (
        Reunion.objects
        .filter(_scope_user(request.user), date_r=d)
        .order_by("heure_r", "titre")
        .distinct()
    )
    payload = {
        "date": d.isoformat(),
        "meetings": [{
            "id": r.id,
            "titre": r.titre,
            "date": r.date_r.isoformat(),
            "heure": r.heure_r.strftime("%H:%M"),
            "status": r.status,
            "status_label": r.get_status_display(),
        } for r in qs]
    }
    return JsonResponse(payload)

# ------------------------
# POST: créer une réunion
# ------------------------

@login_required
def calendar_create(request):
    """Crée une réunion planifiée via la modale."""
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

# ------------------------
# JSON: détail d’une réunion (pour la modale Gérer)
# ------------------------

@login_required
def calendar_meeting_info(request, pk: int):
    r = get_object_or_404(Reunion.objects.select_related("utilisateur"), pk=pk)

    # lecture autorisée : créateur / participant / superuser
    if not (r.utilisateur_id == request.user.id
            or r.participants.filter(id=request.user.id).exists()
            or request.user.is_superuser):
        return HttpResponseForbidden("Accès refusé")

    users = User.objects.all().order_by("first_name", "last_name", "username")
    selected_ids = set(r.participants.values_list("id", flat=True))

    payload = {
        "id": r.id,
        "titre": r.titre,
        "date": r.date_r.isoformat(),
        "heure": r.heure_r.strftime("%H:%M"),
        "status": r.status,
        "status_label": r.get_status_display(),
        "participants": list(selected_ids),
        "participants_all": [
            {"id": u.id, "label": _user_label(u), "selected": (u.id in selected_ids)}
            for u in users
        ],
        "can_edit": (r.utilisateur_id == request.user.id) or request.user.is_superuser,
    }
    return JsonResponse(payload)

# ------------------------
# POST: mettre à jour date/heure/participants
# ------------------------

@login_required
def calendar_meeting_update(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Méthode non supportée")

    rid = request.POST.get("id")
    r = get_object_or_404(Reunion, id=rid)

    # Seul le créateur (ou superuser) peut modifier
    if not (r.utilisateur_id == request.user.id or request.user.is_superuser):
        return HttpResponseForbidden("Seul le créateur peut modifier")

    d = parse_date(request.POST.get("date") or "")
    t = _parse_hhmm(request.POST.get("heure") or "")

    if d:
        r.date_r = d
    if t:
        r.heure_r = t
    r.save(update_fields=["date_r", "heure_r"])

    # participants
    ids = request.POST.getlist("participants")
    if ids:
        r.participants.set(User.objects.filter(id__in=ids))
    else:
        r.participants.clear()

    return JsonResponse({"ok": True})

# ------------------------
# POST: démarrer la réunion -> statut en_cours + redirection transcription
# ------------------------

@login_required
def calendar_start(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Méthode non supportée")

    rid = request.POST.get("id")
    r = get_object_or_404(Reunion, id=rid)

    # Autorisation : créateur ou superuser
    if not (r.utilisateur_id == request.user.id or request.user.is_superuser):
        return HttpResponseForbidden("Seul le créateur peut démarrer la réunion")

    # Optionnel: mettre à jour date/heure depuis la modale avant de démarrer
    d = parse_date(request.POST.get("date") or "")
    t = _parse_hhmm(request.POST.get("heure") or "")
    if d:
        r.date_r = d
    if t:
        r.heure_r = t

    r.status = "en_cours"
    r.save(update_fields=["date_r", "heure_r", "status"])

    # Redirection vers la page de transcription
    try:
        redirect_url = reverse("transcription")  # adapte le nom si besoin
    except NoReverseMatch:
        redirect_url = "/transcription/"
    # on passe l'id pour contexte
    if r.date_r==datetime.date.today():
        redirect_url = f"{redirect_url}/{r.id}/"
    else:
        redirect_url=f"/calendar/"

    return JsonResponse({"ok": True, "redirect": redirect_url})
def view_meeting(request, meeting_id: int):
    """
    Page détail d'une réunion :
    - Infos (titre, date, heure, statut)
    - Participants
    - Audios (liste + durée totale)
    - Transcription / Résumé / Rapport si existants
    Accès : créateur OU participant.
    """
    meeting = get_object_or_404(Reunion.objects.select_related("utilisateur"), id=meeting_id)

    # Permission : créateur ou participant
    is_owner = (meeting.utilisateur_id == request.user.id)
    is_participant = meeting.participants.filter(id=request.user.id).exists()
    if not (is_owner or is_participant or request.user.is_superuser):
        return HttpResponseForbidden("Vous n'avez pas accès à cette réunion.")

    # Audios & durée totale (en heures)
    audios = meeting.audios.all().order_by("-id")  # related_name="audios"
    total_seconds = audios.aggregate(s=Sum("duree")).get("s") or 0
    total_hours = round(total_seconds / 3600, 2)

    # Liens 1-1 : transcription -> résumé -> rapport (si présents)
    transcription = getattr(meeting, "transcription", None)
    resume = getattr(transcription, "resume", None) if transcription else None
    rapport = getattr(resume, "rapport", None) if resume else None

    ctx = {
        "meeting": meeting,
        "is_owner": is_owner,
        "participants": meeting.participants.all(),
        "audios": audios,
        "total_audio_seconds": total_seconds,
        "total_audio_hours": total_hours,
        "transcription": transcription,
        "resume": resume,
        "rapport": rapport,
    }
    return render(request, "HTML/meeting_detail.html", ctx)

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
@login_required
def generate_report(request, reunion_id: int):
    """
    Crée un rapport DOCX avec infos réunion + résumé + transcription, puis l'attache à Rapport.fichier.
    Nécessite `python-docx`:  pip install python-docx
    """
    

    reunion = get_object_or_404(Reunion, pk=reunion_id, utilisateur=request.user)
    tr = getattr(reunion, "transcription", None)
    rs = getattr(tr, "resume", None) if tr else None

    if not tr:
        messages.error(request, "Aucune transcription enregistrée pour cette réunion.")
        return redirect("transcription_page", reunion_id=reunion.id)

    doc = Document()
    doc.add_heading("Rapport de réunion", level=1)

    # (Optionnel) logo d'entreprise
    # place un logo dans settings.MEDIA_ROOT / 'logo.png' par ex
    logo_path = os.path.join(getattr(settings, "MEDIA_ROOT", ""), "logo.png")
    if os.path.exists(logo_path):
        try:
            doc.add_picture(logo_path, width=Inches(1.2))
        except Exception:
            pass

    # Meta
    doc.add_paragraph(f"Titre : {reunion.titre}")
    doc.add_paragraph(f"Date : {reunion.date_r.strftime('%d/%m/%Y')} à {reunion.heure_r.strftime('%H:%M')}")
    doc.add_paragraph(f"Statut : {reunion.get_status_display()}")

    # Participants
    if reunion.participants.exists():
        doc.add_paragraph("Participants :", style='List Bullet')
        for u in reunion.participants.all():
            doc.add_paragraph(f"- {u.get_full_name() or u.username}", style='List Bullet')

    # Résumé
    if rs:
        doc.add_heading("Résumé", level=2)
        doc.add_paragraph(rs.text_resume)

    # Transcription
    doc.add_heading("Transcription", level=2)
    doc.add_paragraph(tr.text_transcrit)

    # Sauvegarde temporaire puis attach à Rapport.fichier
    with NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        doc.save(tmp.name)
        tmp.flush()
        tmp_path = tmp.name

    # upsert Rapport
    rp, created = Rapport.objects.get_or_create(resume=rs if rs else None)
    # s'il n'y a pas de résumé, on peut lier un rapport "basé uniquement sur transcription"
    if not rs:
        # pour respecter ton schéma (rapport -> OneToOne(Resume)), on peut créer un résumé minimal :
        rs = Resume.objects.create(transcription=tr, text_resume="(Résumé non fourni)")
        rp, created = Rapport.objects.get_or_create(resume=rs)

    with open(tmp_path, "rb") as f:
        rp.fichier.save(f"rapport_reunion_{reunion.id}.docx", File(f), save=True)

    os.remove(tmp_path)
    messages.success(request, "Rapport généré et attaché à la réunion.")
    return redirect("view_meeting", meeting_id=reunion.id)
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings

from .models import Reunion, Transcription, Resume, Rapport
