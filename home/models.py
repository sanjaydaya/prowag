from django.db import models
from django.utils import timezone
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail.blocks import CharBlock, RichTextBlock, StructBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtailmetadata.models import MetadataPageMixin
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import Tag, TaggedItemBase
from django.core.exceptions import ValidationError
from datetime import date

# Validators
def validate_future_date(value):
    if value < date.today():
        raise ValidationError("Date must be in the future.")

# Abstract Model for common fields
class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

# Snippet Models
@register_snippet
class Footer(BaseModel):
    content = RichTextField()
    panels = [FieldPanel('content')]

    def __str__(self):
        return "Global Footer"

@register_snippet
class ContactInformation(BaseModel):
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    panels = [
        FieldPanel('email'),
        FieldPanel('phone'),
        FieldPanel('address'),
    ]

    def __str__(self):
        return "Contact Information"

@register_snippet
class Sponsor(BaseModel):
    name = models.CharField(max_length=255)
    image = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='sponsors_images'
    )
    code_snippet = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(blank=True, null=True, verbose_name="Sponsor Link")
    order = models.PositiveIntegerField(default=0, verbose_name="Display Order")
    panels = [
        FieldPanel('name'),
        FieldPanel('image'),
        FieldPanel('code_snippet'),
        FieldPanel('link'),
        FieldPanel('order'),
    ]

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

@register_snippet
class Testimonial(BaseModel):
    name = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='testimonials_images'
    )
    panels = [
        FieldPanel('name'),
        FieldPanel('text'),
        FieldPanel('image'),
    ]

    def __str__(self):
        return self.name

@register_snippet
class SocialMediaLink(BaseModel):
    platform_name = models.CharField(max_length=50)
    url = models.URLField()
    panels = [
        FieldPanel('platform_name'),
        FieldPanel('url'),
    ]

    def __str__(self):
        return self.platform_name

@register_snippet
class TeamMember(BaseModel):
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    image = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='team_member_images'
    )
    panels = [
        FieldPanel('name'),
        FieldPanel('role'),
        FieldPanel('bio'),
        FieldPanel('image'),
    ]

    def __str__(self):
        return self.name

class FAQBlock(StructBlock):
    question = CharBlock(max_length=255)
    answer = RichTextBlock()

    class Meta:
        icon = 'help'
        template = 'blocks/faq_block.html'

@register_snippet
class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey('BlogPost', related_name='tagged_items')

@register_snippet
class BlogPost(BaseModel, ClusterableModel):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    body = RichTextField()
    date_published = models.DateField(default=timezone.now)
    image = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='blog_post_images'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="blog_posts")
    panels = [
        FieldPanel('title'),
        FieldPanel('summary'),
        FieldPanel('body'),
        FieldPanel('date_published'),
        FieldPanel('image'),
        FieldPanel('tags'),
    ]

    def __str__(self):
        return self.title

@register_snippet
class Event(BaseModel):
    name = models.CharField(max_length=255)
    description = RichTextField()
    date = models.DateField(validators=[validate_future_date])
    location = models.CharField(max_length=255, blank=True, null=True)
    image = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='event_images'
    )
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('date'),
        FieldPanel('location'),
        FieldPanel('image'),
    ]

    def __str__(self):
        return self.name

class HomePage(MetadataPageMixin, Page):
    logo = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='home_page_logo'
    )
    banner_title = models.CharField(max_length=255)
    banner_button_text = models.CharField(max_length=50, default="Click")
    banner_button_link = models.ForeignKey(
        'wagtailcore.Page', null=True, blank=True, on_delete=models.SET_NULL, related_name='home_banner_button_links',
        verbose_name="Banner Button Link"
    )
    banner_image = models.ForeignKey(
        Image, null=True, blank=True, on_delete=models.SET_NULL, related_name='home_banner_images'
    )
    banner_text = models.TextField(blank=True, null=True)
    features = StreamField([('feature', CharBlock(classname="feature-item", icon="list-ul"))], use_json_field=True, blank=True)
    body = StreamField([ 
        ('heading', CharBlock(classname="full title")), 
        ('paragraph', RichTextBlock(classname="full richtext")),
        ('image', ImageChooserBlock(classname="full image"))
    ], use_json_field=True, blank=True)
    marquee_text = models.CharField(max_length=255, blank=True, null=True)
    contact_information = models.ForeignKey(
        ContactInformation, null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    testimonials = models.ManyToManyField(Testimonial, related_name="home_pages", blank=True)
    faqs = StreamField([('faq', FAQBlock())], use_json_field=True, blank=True)
    meta_description = models.CharField(max_length=160, blank=True, null=True)
    meta_keywords = models.CharField(max_length=255, blank=True, null=True)
    google_analytics_code = models.TextField(blank=True, null=True)
    newsletter_form = models.TextField(blank=True, null=True, help_text="Embed HTML form for newsletter subscription")
    custom_header_script = models.TextField(blank=True, null=True, verbose_name="Custom Header Script")
    custom_footer_script = models.TextField(blank=True, null=True, verbose_name="Custom Footer Script")

    content_panels = Page.content_panels + [
        FieldPanel('logo'),
        FieldPanel('banner_title'),
        FieldPanel('banner_button_text'),
        FieldPanel('banner_button_link'),
        FieldPanel('banner_image'),
        FieldPanel('banner_text'),
        FieldPanel('features'),
        FieldPanel('body'),
        FieldPanel('marquee_text'),
        FieldPanel('contact_information'),
        FieldPanel('testimonials'),
        FieldPanel('faqs'),
        FieldPanel('meta_description'),
        FieldPanel('meta_keywords'),
        FieldPanel('google_analytics_code'),
        FieldPanel('newsletter_form'),
        FieldPanel('custom_header_script'),
        FieldPanel('custom_footer_script'),
    ]

    def __str__(self):
        return self.banner_title
