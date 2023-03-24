from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from .models import Post, Comment
from .forms import CommentForm, PostForm


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(featured_flag=True).order_by("-created_on")
    template_name = "index.html"
    paginate_by = 3


class PostDetail(View):
    def get(self, request, slug, *args, **kwargs):
        return render(request, "post_detail.html")


# class PostLike(View):

#     def post(self, request, slug):
#         post = get_object_or_404(Post, slug=slug)

#         if post.likes.filter(id=request.user.id).exists():
#             post.likes.remove(request.user)
#         else:
#             post.likes.add(request.user)
#         return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class About(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "about.html",
            {}
        )


class AddStory(View):
    def get(self, request, *args, **kwargs):
        post_form = PostForm()
        return render(
            request,
            "add_story.html",
            {
                "post_form": post_form,
            }
        )


class Search(View):
    def get(self, request, *args, **kwargs):
        return render(request, "search.html")

    def post(self, request, *args, **kwargs):
        qs = Post.objects.all()
        title_contains_query = request.POST.get('title_contains')
        title_exact_query = request.GET.get('title_exact')
        title_or_author_query = request.GET.get('title_or_author')
        print(title_contains_query)
        if title_contains_query != '' and title_contains_query is not None:
            qs = qs.filter(title__icontains=title_contains_query)
        context = {
            'queryset': qs
        }
        return render(request, "search.html", context)


class MyPage(View):
    def get(self, request, id, *args, **kwargs):
        return render(request, "my_page.html")
