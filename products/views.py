from collections import defaultdict
from django.views import generic
from products.models import AttributeValue, Product, Comments
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify
from django.db.models import Prefetch, Avg , Count
from .forms import CommentForm
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

def post_redirect_view(request, pk):
    product_obj = get_object_or_404(Product, pk=pk)
    return redirect(
        'products:product_detail',
        pk=product_obj.pk,
        slug=slugify(product_obj.full_name, allow_unicode=True),
        permanent=True
    )

class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/product_details.html"
    context_object_name = "product"

    @method_decorator(login_required)
    def post(self,request,*args, **kwargs):
        
        self.object = self.get_object()
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user = request.user
            new_comment.product = self.object
            if comment_form.cleaned_data.get('is_recommend')==None:
                if new_comment.rating >=3:
                    new_comment.is_recommend = True
                else:
                    new_comment.is_recommend = False
            new_comment.save()
            messages.success(request, 'دیدگاه شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود.')
            return redirect(self.object.get_absolute_url())
        else:
            print("Form is invalid:", comment_form.errors)
            context = self.get_context_data(object=self.object,comment_form=comment_form)
            return self.render_to_response(context)
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'parent_product__brand',
            'parent_product__category'
        ).prefetch_related(
                Prefetch(
                'attribute_values',
                queryset=AttributeValue.objects.select_related(
                    'attribute__attribute_category'  
                ).order_by(
                    'attribute__attribute_category__id'  
                ),
                to_attr='sorted_attribute_values' 
                ),
            'parent_product__images',
            'color',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        discount_percentage = 0
        
        if product.discount_price and product.price > 0 and product.price > product.discount_price:
            discount_amount = product.price - product.discount_price
            percentage = (discount_amount / product.price) * 100
            discount_percentage = round(percentage) 
        context['discount_percentage'] = discount_percentage
        grouped_attributes = defaultdict(list)

        for value_obj in self.object.sorted_attribute_values:
            category = value_obj.attribute.attribute_category
            grouped_attributes[category].append(value_obj)
        context['grouped_attributes'] = dict(grouped_attributes)


        comments = Comments.objects.filter(parent_product=product.parent_product,is_approved=True).select_related('user').order_by('-datetime_created')

        comment_summary_data = comments.aggregate(
            average_rating = Avg('rating'),
            comment_count = Count('id'),
        )
        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get('page')
        commnts_filter_by_page_number = paginator.get_page(page_number)

        context['comments'] = commnts_filter_by_page_number
        context['comments_count'] = comment_summary_data.get('comment_count')
        context['average_rating'] = "{:.2f}".format(comment_summary_data.get('average_rating'))


        if 'comment_form' not in context:
            context['comment_form'] = CommentForm()


        return context
    