from django import template
register = template.Library()

@register.filter(name='main_image')
def only_active(queryset):
    return queryset.filter(is_main_image=True).first().image.url

@register.filter(name='non_main_image')
def only_active(queryset):
    return queryset.filter(is_main_image=False).first().image.url