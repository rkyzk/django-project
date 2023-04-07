from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin # UserPassesTestMixin
from .models import Post, Comment
from .forms import CommentForm, PostForm, PhotoForm
from datetime import datetime, timedelta


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(featured_flag=True).order_by("-created_on")
    template_name = "index.html"


class PostMoreStories(generic.ListView):
    model = Post
    queryset = Post.objects.filter(status=2).order_by("-created_on")
    template_name = "more_stories.html"

    # model = Post
    # template_name = "more_stories.html"
    # paginate_by = 6

    # def get_context_data(self, **kwargs):
    #     context = super(PostMoreStories, self).get_context_data(**kwargs)
    #     queryset = []   # Post.objects.all()
    #     # (published_on > (datetime.now() - timedelta(days=7)).date())
    #     context['posts_this_week'] = queryset
    #     return context


class PostDetail(View):
    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
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
                "comment_form": CommentForm(),
                "update_form": None
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


class AddStory(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(
            request,
            "add_story.html",
            {
                "post_form": PostForm(),
                "photo_form": PhotoForm()
            }
        )

    def post(self, request, *args, **kwargs):
        post_form = PostForm(self.request.POST)
        photo_form = PhotoForm(self.request.POST, self.request.FILES)
        if post_form.is_valid() and photo_form.is_valid():
            post_form.instance.author = self.request.user
            photo = photo_form.save(commit=False)
            post_form.instance.featured_image = photo.image
            if 'submit' in self.request.POST.keys():
                post_form.instance.status = 1
                post_form.save()
                messages.add_message(self.request, messages.SUCCESS, 'Your draft has been submitted.')
            else:
                post_form.save()
                messages.add_message(self.request, messages.SUCCESS, 'Your draft has been saved.')    
        else:
            print("error occured")
        return render(
            request,
            "add_story.html",
            {
                "post_form": PostForm(),
                "photo_form": PhotoForm()
            }
        )


# if post.status == 2:
#                 messages.add_message(self.request, messages.INFO, "You can't update a post that's been published.")
    


class UpdatePost(LoginRequiredMixin, View): # UserPassesTestMixin,

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        original_data = {
                            "title": post.title,
                            "content": post.content,
                            "region": post.region,
                            "category": post.category,
                        }

        image = post.featured_image.image

        return render(
            request,
            "update_post.html",
            {
                "post_form": PostForm(initial=original_data),
                "photo_form": PhotoForm(image),
                "post": post
            }
        )


    def post(self, request, slug, *args, **kwargs):

        post = get_object_or_404(Post, slug=slug)
        post_form = PostForm(self.request.POST, instance=post)
        photo_form = PhotoForm(self.request.POST, self.request.FILES)
        
        if post_form.is_valid() and photo_form.is_valid:
            post_form.instance.author = self.request.user
            photo = photo_form.save(commit=False)
            # if photo.image is None:
            #     post_form.instance.featured_image = post.featured_image
            # else:
            post_form.instance.featured_image = photo.image

            if 'submit' in self.request.POST.keys():
                post_form.instance.status = 1
                post_form.save()
                messages.add_message(self.request, messages.SUCCESS, 'Your draft has been submitted.')
            else:
                post_form.save()
                messages.add_message(self.request, messages.SUCCESS, 'Your draft has been saved.')

        else:
            print ("error occured")
            print ("non",post_form.non_field_errors())   
            field_errors = [ (field.label, field.errors) for field in post_form]
            print ("field", field_errors)
            print (post_form.errors)
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


    # def test_func(self):
    #     post = get_object_or_404(Post, slug=slug)
    
    #     if self.request.user == post.author:
    #         return True
    #     return False

# class DeletePost(LoginRequiredMixin, generic.DeleteView): # UserPassesTestMixin, 
#     model = Post
#     template_name = "confirm_delete.html"
#     success_url = '/'


#     def test_func(self):
#         post = self.get_object()
#         if self.request.user == post.author:
#             return True
#         return False


class DeletePost(View):

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        post.delete()
        messages.add_message(self.request, messages.SUCCESS, 'Your draft has been deleted.')
        return HttpResponseRedirect(reverse('home'))


class UpdateComment(View):

    def get(self, request, id, *args, **kwargs):
        comment = get_object_or_404(Comment, id=id)
        update_form = CommentForm(instance=comment)
        comment_form = CommentForm()
        slug = comment.post.slug

        return render(
            request,
            "post_detail.html",
            {
                "comment_form": comment_form,
                "update_form": update_form
            }
        )


    def post(self, request, id, *args, **kwargs):

        comment = get_object_or_404(Comment, id=id)
        comment_form = CommentForm(self.request.POST, instance=comment)
        updated = comment_form.save(commit=False)
        updated.name = request.user
        updated.comment_status = 1
        slug = comment.post.slug
        if comment_form.is_valid():
            updated.save()
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class DeleteComment(View):

    def post(self, request, id, *args, **kwargs):
        comment = get_object_or_404(Comment, id=id)
        comment.comment_status = 2
        slug = comment.post.slug
        comment.save()
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class Search(View):
    def get(self, request, *args, **kwargs):
        qs = []
        category_choices = Post._meta.get_field('category').choices
        categories = [cat[1] for cat in category_choices]
        region_choices = Post._meta.get_field('region').choices
        regions = [region[1] for region in region_choices]
        category = request.GET.get('category')

        posts = Post.objects.all()
        title_query = request.GET.get('title_input')
        title_filter_type = request.GET.get('title_option')
        author_query = request.GET.get('author_input')
        author_filter_type = request.GET.get('author_filter')
        kw_query_list = [request.GET.get('keyword_1'),
                         request.GET.get('keyword_2'),
                         request.GET.get('keyword_3')
                    ]
        
        # selected_label = DROP1_DICT[selected_value]
        # print(selected_value)
        # print(selected_label)
        # content_contains_query = request.GET.get('content_contains')
        # author_contains_query = request.GET.get('author_contains')
        # author_exact_query = request.GET.get('author_exact')
    
        # liked_count_min_query = request.GET.get('liked_count_min')
        # pub_date_min_query = request.GET.get('date_min')
        # pub_date_max_query = request.GET.get('date_max')
        
        # category = request.GET.get('category')
        # region = request.GET.get('region')

        qs_kw = []
        query_lists = [title_query, author_query, qs_kw]
        for kw in kw_query_list:
            if kw != '' and kw is not None:
                qs = posts.filter(Q(title_icontains=kw) and Q(content_icontains=kw))
                qs_kw.append(qs)
        if qs_kw == []:
            query_lists.remove(qs_kw)

        if title_query is None:   # not necessary to say is None or != ''
            query_lists.remove(title_query)
        else:
            if title_filter_type == "contains":
                qs_title = posts.filter(title__icontains=title_query)
            else:
                qs_title = posts.filter(title__exact=title_query)

        if author_query is None:
            query_lists.remove(author_query)
        else:
            if author_filter_type == "contains":
                qs_author = posts.filter(author__username__icontains=author_query)
            else:
                qs_author = posts.filter(author__username__exact=author_query)

        i = 0
        if query_lists != []:
            qs = query_lists[0]
            for i in range(len(query_lists) - 1):
                print("hi")
                qs = [post for post in query_lists[i] if post in query_lists[i+1]]
                i += 1

            print(qs)
        # elif author_exact_query != '' and author_exact_query is not None:
        #     qs = posts.filter(author__username__exact=author_exact_query)

        # elif pub_date_min_query != '' and pub_date_min_query is not None:
        #     min_date_str = pub_date_min_query + ' 00:00:00.000000+00:00'
        #     print(f'min_date_str: ' + min_date_str)
        #     min_date = datetime.strptime(min_date_str, '%Y-%m-%d %H:%M:%S.%f%z')
        #     print(type(min_date))
        #     print(min_date)
        #     # qs = posts.filter(published_on >= min_date)
        #     # print(qs)

        # elif liked_count_min_query:
        #     qs = [post for post in posts if (post.number_of_likes() >= int(liked_count_min_query))]

        # elif region != 'Choose...':
        #     qs = [post for post in posts if post.get_region_display() == region]
        # elif category != 'Choose...':
        #     qs = [post for post in posts if post.get_category_display() == category]
        # # if qs = []:
        #    # no_posts = "No posts found"
        # else:
        #     qs = []
        # context = {
        #     'queryset': qs,
        #     # 'no_posts': no_posts
        # }
        # return render(request, "search.html", context)

        context = {
            'categories': categories,
            'regions': regions,
            'queryset': qs,
        }
        return render(request, "search.html", context)

    # def post(self, request, *args, **kwargs):
    #     posts = Post.objects.all()
    #     title_contains_query = request.POST.get('title_contains')
    #     title_exact_query = request.POST.get('title_exact')
    #     content_contains_query = request.POST.get('content_contains')
    #     author_contains_query = request.POST.get('author_contains')
    #     author_exact_query = request.POST.get('author_exact')
    
    #     liked_count_min_query = request.POST.get('liked_count_min')
    #     pub_date_min_query = request.POST.get('date_min')
    #     pub_date_max_query = request.POST.get('date_max')
        
    #     category = request.POST.get('category')
    #     region = request.POST.get('region')

    #     if title_contains_query != '' and title_contains_query is not None:
    #         qs = posts.filter(title__icontains=title_contains_query)

    #     elif title_exact_query != '' and title_exact_query is not None:
    #         qs = posts.filter(title__exact=title_exact_query)

    #     elif content_contains_query != '' and content_contains_query is not None:
    #         qs = posts.filter(content__icontains=content_contains_query)

    #     elif author_contains_query != '' and author_contains_query is not None:
    #         qs = posts.filter(author__username__icontains=author_contains_query)

    #     elif author_exact_query != '' and author_exact_query is not None:
    #         qs = posts.filter(author__username__exact=author_exact_query)

    #     elif pub_date_min_query != '' and pub_date_min_query is not None:
    #         min_date_str = pub_date_min_query + ' 00:00:00.000000+00:00'
    #         print(f'min_date_str: ' + min_date_str)
    #         min_date = datetime.strptime(min_date_str, '%Y-%m-%d %H:%M:%S.%f%z')
    #         print(type(min_date))
    #         print(min_date)
    #         # qs = posts.filter(published_on >= min_date)
    #         # print(qs)

    #     elif liked_count_min_query:
    #         qs = [post for post in posts if (post.number_of_likes() >= int(liked_count_min_query))]

    #     elif region != 'Choose...':
    #         qs = [post for post in posts if post.get_region_display() == region]
    #     elif category != 'Choose...':
    #         qs = [post for post in posts if post.get_category_display() == category]
    #     # if qs = []:
    #        # no_posts = "No posts found"
    #     else:
    #         qs = []
    #     context = {
    #         'queryset': qs,
    #         # 'no_posts': no_posts
    #     }
    #     return render(request, "search.html", context)


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
