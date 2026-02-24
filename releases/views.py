from django.shortcuts import render, redirect, get_object_or_404
from .models import ReleasePost, Artist, Event, AffiliateLink, ChatMessage
from .forms import ReleaseUploadForm
import json


def release_list(request, tag=None):
    if tag:
        posts = ReleasePost.objects.filter(tags__icontains=tag).order_by('-release_datetime')
    else:
        posts = ReleasePost.objects.order_by('-release_datetime')
    
    return render(request, 'releases/release_list.html', {
        'posts': posts,
        'active_tag': tag,
    })


def release_detail(request, slug):
    post = get_object_or_404(ReleasePost, slug=slug)
    return render(request, 'releases/release_detail.html', {'post': post})


def upload_release(request):
    if request.method == 'POST':
        form = ReleaseUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('release_list')
    else:
        form = ReleaseUploadForm()
    return render(request, 'releases/upload_release.html', {'form': form})


def homepage(request):
    return render(request, "index.html")


def artists(request):
    artist_list = Artist.objects.all()
    return render(request, "artists.html", {'artists': artist_list})


def contact(request):
    return render(request, "contact.html")


def merch(request):
    return render(request, 'merch.html')


def events(request, tag=None):
    if tag:
        event_list = Event.objects.filter(tags__icontains=tag).order_by('-event_date')
    else:
        event_list = Event.objects.order_by('-event_date')
    return render(request, 'events.html', {
        'events': event_list,
        'active_tag': tag,
    })


def links(request):
    all_links = AffiliateLink.objects.filter(is_active=True)
    categories = {}
    for link in all_links:
        cat = link.get_category_display()
        categories.setdefault(cat, []).append(link)
    return render(request, 'releases/links.html', {
        'categories': categories,
    })


def wall(request):
    # Renamed from 'messages' to avoid conflict with Django's messages framework
    chat_history = list(ChatMessage.objects.order_by('-timestamp')[:100])
    chat_history.reverse()  # oldest first

    chat_history_json = json.dumps([
        {
            "username": m.username,
            "message": m.message,
            "timestamp": m.timestamp.strftime("%H:%M"),
        }
        for m in chat_history
    ])

    return render(request, 'releases/wall.html', {
        'messages_json': chat_history_json,
    })

def password_reset_confirm(request, token):
    from .models import PasswordResetToken
    import hashlib

    try:
        reset = PasswordResetToken.objects.select_related('username').get(token=token)
    except PasswordResetToken.DoesNotExist:
        return render(request, 'releases/password_reset_confirm.html', {'error': 'Invalid or expired reset link.'})

    if not reset.is_valid():
        return render(request, 'releases/password_reset_confirm.html', {'error': 'This reset link has expired. Please request a new one.'})

    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')
        if len(password) < 4:
            return render(request, 'releases/password_reset_confirm.html', {
                'token': token, 'error': 'Password must be at least 4 characters.'
            })
        if password != confirm:
            return render(request, 'releases/password_reset_confirm.html', {
                'token': token, 'error': 'Passwords do not match.'
            })
        # Hash and save new password
        import secrets, hashlib
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((salt + password).encode()).hexdigest()
        entry = reset.username
        entry.password_hash = f"{salt}:{hashed}"
        entry.save(update_fields=['password_hash'])
        reset.used = True
        reset.save(update_fields=['used'])
        return render(request, 'releases/password_reset_confirm.html', {'success': True, 'username': entry.username})

    return render(request, 'releases/password_reset_confirm.html', {'token': token})
