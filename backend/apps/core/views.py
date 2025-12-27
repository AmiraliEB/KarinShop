from django.views import generic


class HomePageView(generic.TemplateView):
    template_name = "core/index.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['attr'] = [str(attr) for attr in Product.objects.get.attribute_values.all()]
        return context
