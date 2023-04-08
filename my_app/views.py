from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .models import Post, Comment
from .forms import CommentForm, PostForm, PhotoForm
from datetime import datetime, timedelta, timezone


class PostList(generic.ListView):
    model = Post
    queryset = Post.objects.filter(featured_flag=True).order_by("-created_on")
    template_name = "index.html"


class PostMoreStories(generic.ListView):
    model = Post
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)
    queryset = Post.objects.filter(Q(status=2) & Q(published_on__date__gte=utc_now.date()-timedelta(days=7)) ).order_by("-created_on")
    template_name = "more_stories.html"
    paginate_by = 6


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
    


class UpdatePost(LoginRequiredMixin, View): # UserPassesTestMixin

    def get(self, request, slug, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug)
        # Not Working at all
        # if post.status == 2:
        #     messages.add_message(self.request, messages.INFO, "You can't update a post that's been published.")
        #     return HttpResponseRedirect(reverse('post_detail', args=[slug]))
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
    
    def test_func(self):
        return self.get_object().author == self.request.user


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

            print(self.request.POST.keys())
            if 'submit' in self.request.POST.keys():
                post_form.instance.status = 1
                post_form.save()
                messages.add_message(self.request, messages.SUCCESS, 'Your draft has been submitted.')
            else:
                post_form.save()
                messages.add_message(self.request, messages.SUCCESS, 'Your draft has been saved.')

        else:
            meessages.add_message(self.request, messages.INFO, "Error occured.  The change hasn't been saved.")
            print ("error occured")
            print ("non", post_form.non_field_errors())   
            field_errors = [(field.label, field.errors) for field in post_form]
            print ("field", field_errors)
            print (post_form.errors)
        return HttpResponseRedirect(reverse('post_detail', args=[slug]))


class DeletePost(View):  # UserPassesTestMixin, 

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

        posts = Post.objects.filter(status=2)
        print("published date")
        print(posts[0].published_on)
        print(type(posts[0].published_on))

        title_query = request.GET.get('title_input')
        title_filter_type = request.GET.get('title_option')
        author_query = request.GET.get('author_input')
        author_filter_type = request.GET.get('author_filter')
        kw_query_list = [request.GET.get('keyword_1'),
                         request.GET.get('keyword_2'),
                         request.GET.get('keyword_3')
                    ]   
    
        min_liked_query = request.GET.get('liked_count_min')
        pub_date_min_query = request.GET.get('date_min')
        pub_date_max_query = request.GET.get('date_max')
        
        category = request.GET.get('category')
        region = request.GET.get('region')

        qs_kw = []
        query_lists = []
        for kw in kw_query_list:
            if kw != '' and kw is not None:
                qs = posts.filter(Q(title__icontains=kw) | Q(content__icontains=kw))
                query_lists.append(qs)

        if title_query != '' and title_query is not None:  
            if title_filter_type == "contains":
                qs_title = posts.filter(title__icontains=title_query)
            else:
                qs_title = posts.filter(title__exact=title_query)
            if qs_title != []:
                query_lists.append(qs_title)

        if author_query != '' and author_query is not None:
            if author_filter_type == "contains":
                qs_author = posts.filter(author__username__icontains=author_query)
            else:
                qs_author = posts.filter(author__username__exact=author_query)
            if qs_author != []:
                query_lists.append(qs_author)
       
        if pub_date_min_query != '' and pub_date_min_query is not None:
            min_date_str = pub_date_min_query
            min_date = datetime.strptime(min_date_str, '%Y-%m-%d')
            qs_min_pub_date = posts.filter(published_on__date__gte=min_date)
            query_lists.append(qs_min_pub_date)
        if pub_date_max_query != '' and pub_date_max_query is not None:
            max_date_str = pub_date_max_query
            max_date = datetime.strptime(max_date_str, '%Y-%m-%d')
            qs_max_pub_date = posts.filter(published_on__date__lte=max_date)
            query_lists.append(qs_max_pub_date)

        if min_liked_query != '' and min_liked_query is not None:
            print('hello liked')
            qs_liked = [post for post in posts if (post.number_of_likes()>=int(min_liked_query))]
            print(qs_liked)
            if qs_liked != []:
                query_lists.append(qs_liked)

        if region != 'Choose...':
            qs_region = [post for post in posts if post.get_region_display() == region]
            query_lists.append(qs_region)
        if category != 'Choose...':
            qs_category = [post for post in posts if post.get_category_display() == category]
            query_lists.append(qs_category)

        if query_lists != []:
            qs = query_lists[0]
            if len(query_lists) > 1:
                print("hello")
                i = 0
                for i in range(len(query_lists) - 1):
                    print("hi")
                    qs = [post for post in query_lists[i] if post in query_lists[i+1]]
                    i += 1

        no_results = False
        print(dir(self.request.GET.keys()))
        print(self.request.GET.values())
        if 'submit' in self.request.GET.keys():
            if qs == []:
                no_results = True

        context = {
            'categories': categories,
            'regions': regions,
            'queryset': qs,
            'no_results': no_results
        }
        return render(request, "search.html", context)


class MyPage(LoginRequiredMixin, View):
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
