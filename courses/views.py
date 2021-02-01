from http import HTTPStatus
import pytz
import logging
import json
from http import HTTPStatus
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.utils.timezone import is_aware
from django.contrib.auth import get_user
from django.http import HttpResponse


from courses.models import Event, ConnectionPlatform, Bookmark, CertificateRequest, Certificate, Comment
from profiles.models import ContactMethod, AcceptedCrypto, Profile
from profiles.utils import academia_blockchain_timezones
from star_ratings.models import Rating

logger = logging.getLogger('app_logger')

"""
HTML RENDERS
"""


def event_index(request):
    template = "courses/events.html"
    events = Event.objects.filter(deleted=False)
    logger.info("events: %s" % events)
    logger.warning("HEROKU LOGS WARNING!")
    logger.info("HEROKU LOGS INFO!")

    context = {"events": events, "event_index_active": "active"}
    return render(request, template, context)


def event_detail(request, event_id):
    template = "courses/event_detail.html"
    event = get_object_or_404(Event, id=event_id)
    logger.info("event: %s" % event)

    contact_methods = ContactMethod.objects.filter(user=event.owner, deleted=False)
    accepted_cryptos = AcceptedCrypto.objects.filter(user=event.owner, deleted=False)
    owner_profile = Profile.objects.get(user=event.owner)

    logger.info("contact_methods: %s" % contact_methods)
    logger.info("contact_methods: %s" % contact_methods)
    logger.info("contact_methods: %s" % contact_methods)

    academia_blockchain_timezones()

    event_user_timezone = None
    logged_user_profile = None
    event_is_bookmarked = False
    if request.user.is_authenticated:
        logged_user_profile = Profile.objects.get(user=request.user)
        try:
            user_timezone = pytz.timezone("America/Guayaquil")
            event_user_timezone = event.date_start.astimezone(user_timezone)
        except Exception as e:
            pass

        event_is_bookmarked = Bookmark.objects.filter(event=event, user=request.user, deleted=False).exists()

    logger.info("event_user_timezone: %s" % event_user_timezone)
    logger.info("logged_user_profile: %s" % logged_user_profile)
    logger.info("event_is_bookmarked: %s" % event_is_bookmarked)

    is_event_owner = (event.owner == request.user)
    event_bookmarks = Bookmark.objects.none()
    certificate_requests = CertificateRequest.objects.none()

    logger.info("is_event_owner: %s" % is_event_owner)
    if is_event_owner:
        event_bookmarks = Bookmark.objects.filter(event=event, deleted=False)
        certificate_requests = CertificateRequest.objects.filter(event=event, deleted=False)
        logger.info("event_bookmarks: %s" % event_bookmarks)

    logger.info("certificate_requests: %s" % certificate_requests)

    comments = Comment.objects.filter(event=event, deleted=False)
    rating = Rating.objects.for_instance(event)

    context = {"event": event, "contact_methods": contact_methods, "accepted_cryptos": accepted_cryptos,
               "owner_profile": owner_profile, "event_user_timezone": event_user_timezone,
               "logged_user_profile": logged_user_profile, "event_is_bookmarked": event_is_bookmarked,
               "is_event_owner": is_event_owner, "event_bookmarks": event_bookmarks,
               "certificate_requests": certificate_requests, "comments": comments, 'rating': rating}
    return render(request, template, context)


def event_recorded_online(request):
    template = "courses/event_recorded_online.html"
    context = {"event_index_active": "active"}
    return render(request, template, context)


def event_recurrent_localized(request):
    template = "courses/event_recurrent_localized.html"
    context = {"event_index_active": "active"}
    return render(request, template, context)


def event_singular_online(request):
    template = "courses/event_singular_online.html"
    context = {"event_index_active": "active"}
    return render(request, template, context)


@login_required
def event_create(request):
    if request.method == "GET":
        template = "courses/event_create.html"
        platforms = ConnectionPlatform.objects.filter(deleted=False)
        logger.info("platforms: %s" % platforms)

        context = {"event_index_active": "active", "platforms": platforms}
        return render(request, template, context)

    elif request.method == "POST":
        event_type_description = request.POST.get("event_type_description")
        event_recurrent = bool(request.POST.get("event_recurrent"))
        title = request.POST.get("title")
        description = request.POST.get("description")
        platform_name = request.POST.get("platform_name")
        other_platform = request.POST.get("other_platform")
        date_start = request.POST.get("date_start")
        date_end = request.POST.get("date_end")
        time_day = request.POST.get("time_day")
        record_date = request.POST.get("record_date")
        schedule_description = request.POST.get("schedule_description")

        logger.info("event_type_description: %s" % event_type_description)
        logger.info("event_recurrent: %s" % event_recurrent)
        logger.info("title: %s" % title)
        logger.info("description: %s" % description)
        logger.info("platform_name: %s" % platform_name)
        logger.info("other_platform: %s" % other_platform)
        logger.info("date_start: %s" % date_start)
        logger.info("date_end: %s" % date_end)
        logger.info("time_day: %s" % time_day)
        logger.info("record_date: %s" % record_date)
        logger.info("schedule_description: %s" % schedule_description)

        # Event Type
        if event_type_description == "pre_recorded":
            is_recorded = True
        elif event_type_description in ["live_course", "event_single"]:
            is_recorded = False
        else:
            is_recorded = False

        if event_type_description in ["pre_recorded", "live_course"]:
            event_type = "COURSE"
        elif event_type_description in ["event_single", "event_recurrent"]:
            event_type = "EVENT"
        else:
            event_type = "COURSE"  # loggear exceptions

        # Connection Platform
        try:
            platform_obj = ConnectionPlatform.objects.get(name=platform_name)
        except Exception as e:
            logger.warning("platform_name: %s" % platform_name)
            platform_obj = None

        # Date & Time
        if len(date_start) > 0:
            date_start = datetime.strptime(date_start, "%d/%m/%Y")
        else:
            date_start = None
        if len(date_end) > 0:
            date_end = datetime.strptime(date_end, "%d/%m/%Y")
        else:
            date_end = None
        if len(time_day) > 0 and date_start is not None:
            time_day = datetime.strptime(time_day, "%I:%M %p")
            date_start.replace(hour=time_day.hour, minute=time_day.minute)

        if len(record_date) > 0:
            record_date = datetime.strptime(record_date, "%d/%m/%Y")
        else:
            record_date = None

        created_event = Event.objects.create(
            event_type=event_type,
            is_recorded=is_recorded,
            is_recurrent=event_recurrent,
            owner=request.user,
            title=title,
            description=description,
            platform=platform_obj,
            other_platform=other_platform,
            date_start=date_start,
            date_end=date_end,
            date_recorded=record_date,
            schedule_description=schedule_description
        )

        # Guardar imagen
        if "event_picture" in request.FILES:
            event_picture = request.FILES['event_picture']
            logger.info("event_picture: %s" % event_picture)
            created_event.image.save(event_picture.name, event_picture)

        return redirect("event_detail", event_id=created_event.id)


@login_required
def event_delete(request, event_id):
    deleted_event = get_object_or_404(Event, id=event_id)
    logger.info("deleted_event: %s" % deleted_event)
    if not request.user == deleted_event.owner:
        return HttpResponse(status=403)

    deleted_event.deleted = True
    deleted_event.save()
    return redirect("profile_events")


@login_required
def event_comment(request, event_id):
    if request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        comment_text = request.POST.get("comment_text", None)
        logger.info("event: %s" % event)
        logger.info("comment_text: %s" % comment_text)
        if comment_text:
            comment = Comment.objects.create(
                event=event,
                user=request.user,
                text=comment_text
            )
            logger.info("comment: %s" % comment)
        return redirect("event_detail", event_id=event.id)
    else:
        return HttpResponse(status=400)


@login_required
def edit_event(request, event_id):
    if request.method == "GET":
        template = "courses/event_edit.html"
        event = get_object_or_404(Event, id=event_id)
        logger.info("event: %s" % event)
        platforms = ConnectionPlatform.objects.filter(deleted=False)
        user_contact_methods = ContactMethod.objects.filter(user=event.owner)

        logger.info("platforms: %s" % platforms)
        logger.info("user_contact_methods: %s" % user_contact_methods)

        context = {"event": event, "platforms": platforms, "user_contact_methods": user_contact_methods}
        return render(request, template, context)

    elif request.method == "POST":
        event = get_object_or_404(Event, id=event_id)

        event_type_description = request.POST.get("event_type_description")
        event_recurrent = bool(request.POST.get("event_recurrent"))
        title = request.POST.get("title")
        description = request.POST.get("description")
        platform_name = request.POST.get("platform_name")
        other_platform = request.POST.get("other_platform")
        date_start = request.POST.get("date_start")
        date_end = request.POST.get("date_end")
        time_day = request.POST.get("time_day")
        record_date = request.POST.get("record_date")
        schedule_description = request.POST.get("schedule_description")

        logger.info("event_type_description: %s" % event_type_description)
        logger.info("event_recurrent: %s" % event_recurrent)
        logger.info("title: %s" % title)
        logger.info("description: %s" % description)
        logger.info("platform_name: %s" % platform_name)
        logger.info("other_platform: %s" % other_platform)
        logger.info("date_start: %s" % date_start)
        logger.info("date_end: %s" % date_end)
        logger.info("time_day: %s" % time_day)
        logger.info("record_date: %s" % record_date)
        logger.info("schedule_description: %s" % schedule_description)

        # Event Type
        if event_type_description == "pre_recorded":
            is_recorded = True
        elif event_type_description in ["live_course", "event_single"]:
            is_recorded = False
        else:
            is_recorded = False

        if event_type_description in ["pre_recorded", "live_course"]:
            event_type = "COURSE"
        elif event_type_description in ["event_single", "event_recurrent"]:
            event_type = "EVENT"
        else:
            event_type = "COURSE"  # loggear exceptions

        # Connection Platform
        try:
            platform_obj = ConnectionPlatform.objects.get(name=platform_name)
        except Exception as e:
            platform_obj = None

        # Date & Time
        if len(date_start) > 0:
            date_start = datetime.strptime(date_start, "%d/%m/%Y")
        else:
            date_start = None
        if len(date_end) > 0:
            date_end = datetime.strptime(date_end, "%d/%m/%Y")
        else:
            date_end = None
        if len(time_day) > 0:
            time_day = datetime.strptime(time_day, "%I:%M %p")
            date_start = date_start.replace(hour=time_day.hour, minute=time_day.minute)
        if len(record_date) > 0:
            record_date = datetime.strptime(record_date, "%d/%m/%Y")
        else:
            record_date = None

        event.event_type = event_type
        event.is_recorded = is_recorded
        event.is_recurrent = event_recurrent
        event.owner = request.user
        event.title = title
        event.description = description
        event.platform = platform_obj
        event.other_platform = other_platform
        event.date_start = date_start
        event.date_end = date_end
        event.date_recorded = record_date
        event.schedule_description = schedule_description
        event.save()

        # Guardar imagen
        if "event_picture" in request.FILES:
            event_picture = request.FILES['event_picture']
            logger.info("event_picture: %s" % event_picture)
            event.image.save(event_picture.name, event_picture)

        return redirect("event_detail", event_id=event.id)

# TODO
# The URL could be /certificate_preview/${transactionId}
# Then, the backend searchs for the transaction in the blockchain and with that data
# create and send the certificate_data in the context.
# Suggestion: certificate_data fields could be: graduate, title, author, description, author-address, date and tx-id
# Suggestion: maybe we could add a boolean such as isTxIdValid
# to know if frontend should show a certificate or 404.
# Finally, consume that values in frontend as variables.
def certificate_preview(request, cert_id):
    # certificate = get_object_or_404(Certificate, id=cert_id)
    template = "courses/certificate_preview.html"
    context = {"certificate": ""}
    return render(request, template, context)

"""
API CALLS
"""


@login_required
@csrf_exempt
def event_bookmark(request, event_id):
    if request.is_ajax() and request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        logger.info("event: %s" % event)
        if Bookmark.objects.filter(event=event, user=request.user, deleted=False).exists():
            return HttpResponse(status=200)
        else:
            if Bookmark.objects.filter(event=event, user=request.user, deleted=True).exists():
                bookmark = Bookmark.objects.get(event=event, user=request.user, deleted=True)
                logger.info("bookmark: %s" % bookmark)
                bookmark.deleted = False
                bookmark.save()
            else:
                Bookmark.objects.create(event=event, user=request.user)
            return HttpResponse(status=201)
    else:
        return HttpResponse(status=403)


@login_required
@csrf_exempt
def remove_bookmark(request, event_id):
    if request.is_ajax() and request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        if Bookmark.objects.filter(event=event, user=request.user, deleted=False).exists():
            bookmark = Bookmark.objects.get(user=request.user, event=event, deleted=False)
            logger.info("bookmark: %s" % bookmark)
            bookmark.deleted = True
            bookmark.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=404)

    else:
        return HttpResponse(status=403)


def certificate_detail(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    cert_data = {
        "id": certificate.id,
        "username": certificate.user.username,
        "first_name": certificate.user.first_name,
        "last_name": certificate.user.last_name,
        "cert_date": certificate.date_created,
        "event_title": certificate.event.title,
        "event_description": certificate.event.description,
        "event_owner_username": certificate.event.owner.username,
        "event_owner_first_name": certificate.event.owner.first_name,
        "event_owner_last_name": certificate.event.owner.last_name,
    }
    return JsonResponse(cert_data)


@login_required
@csrf_exempt
def request_certificate(request, event_id):
    if request.is_ajax() and request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        logger.info("event: %s" % event)
        if CertificateRequest.objects.filter(event=event, user=request.user, deleted=False).exists():
            return HttpResponse(status=200)
        else:
            if CertificateRequest.objects.filter(event=event, user=request.user, deleted=True).exists():
                certificate_request = CertificateRequest.objects.get(event=event, user=request.user, deleted=True)
                logger.info("certificate_request: %s" % certificate_request)
                certificate_request.deleted = False
                certificate_request.save()
            else:
                CertificateRequest.objects.create(event=event, user=request.user)
            return HttpResponse(status=201)
    else:
        return HttpResponse(status=403)


@login_required
@csrf_exempt
def cancel_cert_request(request, event_id):
    if request.is_ajax() and request.method == "POST":
        event = get_object_or_404(Event, id=event_id)
        logger.info("event: %s" % event)
        if CertificateRequest.objects.filter(event=event, user=request.user, deleted=False).exists():
            certificate_request = CertificateRequest.objects.get(event=event, user=request.user, deleted=False)
            logger.info("certificate_request: %s" % certificate_request)
            certificate_request.deleted = True
            certificate_request.save()
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=404)
    else:
        return HttpResponse(status=400)


@login_required
@csrf_exempt
def accept_certificate(request, cert_request_id):
    if request.is_ajax() and request.method == "POST":
        certificate_request = get_object_or_404(CertificateRequest, id=cert_request_id)
        logger.info("certificate_request: %s" % certificate_request)
        if request.user == certificate_request.event.owner:
            if Certificate.objects.filter(event=certificate_request.event, user=certificate_request.user).exists():
                logger.warning("certificate ya existe")
            else:
                cert = Certificate.objects.create(event=certificate_request.event, user=certificate_request.user)
                logger.info("cert: %s" % cert)
            certificate_request.accepted = True
            certificate_request.save()
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)


def reject_certificate(request, cert_request_id):
    if request.is_ajax() and request.method == "POST":
        certificate_request = get_object_or_404(CertificateRequest, id=cert_request_id)
        logger.info("certificate_request: %s" % certificate_request)
        if request.user == certificate_request.event.owner:
            if Certificate.objects.filter(event=certificate_request.event, user=certificate_request.user).exists():
                pass  # No puede rechazar si ya existe el certificado
            else:
                certificate_request.accepted = False
                certificate_request.save()
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=403)
    else:
        return HttpResponse(status=400)
