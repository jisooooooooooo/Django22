from django.shortcuts import render
from .models import Post

def index(request):
    posts = Post.objects.all().order_by('-pk')

    return render(
        request,
        'shopping/index.html',
        {
            'posts': posts,
        }
    )

def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request,
        'shopping/single_post_page.html',
        {
            'post': post,
        }
    )
# Create your views here.
