from django import template
register = template.Library()

@register.filter(name='main_image')
def only_active(queryset):
    return queryset.filter(is_main_image=True).first().image.url