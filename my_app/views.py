from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comment
from .forms import CommentForm, PostForm


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(featured_flag=True).order_by("-created_on")
    template_name = "index.html"
    paginate_by = 3


class PostDetail(View):
    def get(self, request, slug, *args, **kwargs):
        post = Post.objects.filter(slug=slug)[0]
        comments = post.comments.filter(approved=True).order_by('created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        bookmarked = False
        if post.bookmark.filter(id=self.request.user.id).exists():
            bookmarked = True

        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": False,
                "liked": liked,
                "bookmarked": bookmarked,
                "comment_form": CommentForm()
            },
        )

    def post(self, request, slug, *args, **kwargs):
        post = Post.objects.filter(slug=slug)[0]
        comments = post.comments.filter(approved=True).order_by('created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True
        bookmarked = False
        if post.bookmark.filter(id=self.request.user.id).exists():
            bookmarked = True

        comment_form = CommentForm(data=request.POST)

        if comment_form.is_valid():
            comment_form.instance.email = request.user.email
            comment_form.instance.name = request.user
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
        else:
            comment_form = CommentForm()
        return render(
            request,
            "post_detail.html",
            {
                "post": post,
                "comments": comments,
                "commented": True,
                "liked": liked,
                "bookmarked": bookmarked,
                "comment_form": CommentForm()
            },
        )


class PostLike(View):

    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class About(View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "about.html",
            {}
        )


# class AddStory(View):
#     def get(self, request, *args, **kwargs):
#         post_form = PostForm()
#         return render(
#             request,
#             "add_story.html",
#             {
#                 "post_form": post_form,
#             }
#         )

#     def post(self, request, *args, **kwargs):
#         post_form = PostForm(data=request.POST)
#         post = post_form.save(commit=False)
#         if post_form.is_valid():
#             if 'save' in request.POST:
#                 post.status = 0
#                 messages.add_message(request, messages.SUCCESS, 'Your draft was saved.')
#             else:
#                 post.status = 1
#                 messages.add_message(request, messages.SUCCESS, 'Your draft was submitted.')
#             post.save()  
#         return render(request, "add_story.html", {'post_form': PostForm()})

#         def form_valid(self, form):
#             form.instance.author = self.request.user
#             return super().form_valid(form)

class AddStory(LoginRequiredMixin, generic.CreateView):
    model = Post
    template_name = "add_story.html"
    fields = ('title', 'content', 'featured_image', 'region', 'category')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        if 'submit' in self.request.POST.keys():
            form.instance.status = 1
            messages.add_message(self.request, messages.SUCCESS, 'Your draft has been submitted.')
        else:
            messages.add_message(self.request, messages.SUCCESS, 'Your draft has been saved.') 
        return super().form_valid(form)


class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    template_name = "update_post.html"
    fields = ('title', 'content', 'featured_image', 'region', 'category')
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        if 'submit' in self.request.POST.keys():
            form.instance.status = 1
            messages.add_message(self.request, messages.SUCCESS, 'Your draft has been submitted.')
        else:
            messages.add_message(self.request, messages.SUCCESS, 'Your draft has been saved.') 
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    template_name = "confirm_delete.html"
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


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
        queryset = Post.objects.filter(author=id)
        comments = Comment.objects.filter(name=id)
        commented_posts = [comment.post for comment in comments]
        # remove duplicates
        commented_posts = list(dict.fromkeys(commented_posts))
        # this can be made concise
        all_posts = Post.objects.all()
        bookmarked_posts = []
        for post in all_posts:
            if post.bookmark.filter(id=request.user.id).exists():
                bookmarked_posts.append(post)

        return render(
            request,
            "my_page.html",
            {
                "queryset": queryset,
                "commented_posts": commented_posts,
                "bookmarked_posts": bookmarked_posts
            },
        )


class Bookmark(View):
    def post(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)

        if post.bookmark.filter(id=request.user.id).exists():
            post.bookmark.remove(request.user)
        else:
            post.bookmark.add(request.user)
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))
