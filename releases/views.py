from django.shortcuts import render, redirect
from .models import ReleasePost, Artist
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