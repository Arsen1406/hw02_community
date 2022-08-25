from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect
from django.db.models import Count
from .models import Post, Group, User
from .form import PostForm


def index(request):
    main = "Последние обновления на сайте"
    post_list = Post.objects.order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'main': main
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': posts,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author).order_by('-pub_date')
    count = Post.objects.filter(author=author).aggregate(Count('pk'))
    posts_other = Post.objects.exclude(author=author)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'posts_other': posts_other,
        'count': count,
        'author': author,
        'posts': posts
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    count = Post.objects.filter(author_id=post.author_id).aggregate(
        Count('pk')
    )
    context = {
        'count': count,
        'post': post,
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


def post_create(request):
    is_edit = False
    group = Group.objects.all()
    title = request.user.username
    title = User.objects.get(username=title)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = Post()
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            post.author_id = request.user.id
            post.save()
            return HttpResponseRedirect(f'/profile/{title}')
    else:
        form = PostForm

    context = {
        'is_edit': is_edit,
        'title': title,
        'group': group,
        'form': form
    }
    template = 'posts/create_post.html'
    return render(request, template, context)


def post_edit(request, post_id):
    is_edit = True
    group = Group.objects.all()
    user_name = request.user.username
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id == post.author_id:
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post.save()
                return HttpResponseRedirect(f'/profile/{user_name}')
        else:
            form = PostForm
    else:
        return HttpResponseRedirect(f'/posts/{post_id}')
    context = {
        'is_edit': is_edit,
        'group': group,
        'form': form,
        'post': post,
    }
    template = 'posts/create_post.html'
    return render(request, template, context)

# class JustStaticPage(TemplateView):
#     template_name = 'posts/about_author.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['just_title'] = 'Очень простая страница'
#         context['just_text'] = ('На создание этой страницы '
#                                 'у меня ушло пять минут! Ай да я.')
#         return context
