from django.shortcuts import render, redirect, get_object_or_404
from .models import ReleasePost, Artist, Event, AffiliateLink, ChatMessage, ChatUsername
from .forms import ReleaseUploadForm
from django.http import JsonResponse
from django.core import signing
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from PIL import Image
import io
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


# ─── Wall Profile Endpoints ───────────────────────────────────────────────────

def get_profile(request, username):
    """Read-only endpoint to fetch a user's profile data for the Wall."""
    try:
        entry = ChatUsername.objects.get(username__iexact=username)
        return JsonResponse({
            'success': True,
            'username': entry.username,
            'location': entry.location or '',
            'bio': entry.bio or '',
            'avatar_url': entry.avatar.url if entry.avatar else None,
            'last_login': entry.last_login.strftime('%b %d, %Y %I:%M %p') if entry.last_login else 'Never'
        })
    except ChatUsername.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)


@csrf_exempt
def update_profile(request):
    """Authenticated endpoint to update bio, location, and handle Avatar uploads."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    # Authenticate via the same token stored in localStorage
    token = request.POST.get('token')
    if not token:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        username = signing.loads(token, max_age=60*60*24*30)
        entry = ChatUsername.objects.get(username__iexact=username)
    except Exception:
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)

    # Update text fields
    location = request.POST.get('location')
    bio = request.POST.get('bio')
    
    if location is not None:
        entry.location = location[:100]
    if bio is not None:
        entry.bio = bio[:500]

    # Handle Avatar Image Resizing
    if 'avatar' in request.FILES:
        avatar_file = request.FILES['avatar']
        try:
            img = Image.open(avatar_file)
            img = img.convert('RGBA')  # Preserve transparency
            img.thumbnail((120, 120))  # Crush to a small square
            
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='PNG')
            
            filename = f"{entry.username}_avatar.png"
            entry.avatar.save(filename, ContentFile(thumb_io.getvalue()), save=False)
        except Exception as e:
            return JsonResponse({'error': 'Invalid image file.'}, status=400)

    entry.save()
    
    return JsonResponse({
        'success': True, 
        'avatar_url': entry.avatar.url if entry.avatar else None
    })