from django.shortcuts import render, redirect
from .models import ReleasePost, Artist, Event
from .forms import ReleaseUploadForm

def release_list(request, tag=None):
    if tag:
        posts = ReleasePost.objects.filter(tags__icontains=tag).order_by('-release_datetime')
    else:
        posts = ReleasePost.objects.order_by('-release_datetime')
    
    return render(request, 'releases/release_list.html', {
        'posts': posts,
        'active_tag': tag,
    })

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
    # Fetch all artists from the database, ordered by display_order and name
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
    from .models import AffiliateLink
    all_links = AffiliateLink.objects.filter(is_active=True)
    
    # Group by category
    categories = {}
    for link in all_links:
        cat = link.get_category_display()
        categories.setdefault(cat, []).append(link)
    
    return render(request, 'releases/links.html', {
        'categories': categories,
    })


def wall(request):
    from .models import ChatMessage
    import json

    # Load last 100 messages for initial render
    messages = list(
        ChatMessage.objects.order_by('-timestamp')[:100]
    )
    messages.reverse()  # oldest first

    messages_json = json.dumps([
        {
            "username": m.username,
            "message": m.message,
            "timestamp": m.timestamp.strftime("%H:%M"),
        }
        for m in messages
    ])

    return render(request, 'releases/wall.html', {
        'messages_json': messages_json,
    })