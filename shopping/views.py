from django.views.generic import ListView, DetailView
from .models import Post

class PostList(ListView):
    model = Post
    ordering = '-pk'

class PostDetail(DetailView):
    model = Post

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
