from django.shortcuts import render
from .models import HomePage, Footer, SocialMediaLink, BlogPost

def home_page_view(request):
    homepage = HomePage.objects.live().public().first()
    footer = Footer.objects.first()
    social_media_links = SocialMediaLink.objects.all()
    blog_posts = BlogPost.objects.live().public()[:5]

    return render(request, 'home/home_page.html', {
        'page': homepage,
        'footer': footer,
        'social_media_links': social_media_links,
        'blog_posts': blog_posts,
    })
