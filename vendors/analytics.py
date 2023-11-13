from django.db.models import Sum, Count
from payment.models import Order, OrderItem
from product.models import Product
from django.db.models import Sum, OuterRef, Subquery, IntegerField
from django.db.models.functions import Coalesce

def get_total_sales_for_vendor(vendor_id):
    return OrderItem.objects.filter(product__vendor_id=vendor_id).aggregate(total_sales=Sum('price'))

def get_most_sold_items_for_vendor(vendor_id):
    return OrderItem.objects.filter(product__vendor_id=vendor_id).values('product__title').annotate(total_sold=Sum('quantity')).order_by('-total_sold')

def get_repeat_customers_for_vendor(vendor_id):
    return Order.objects.filter(items__product__vendor_id=vendor_id).values('customer').annotate(total_orders=Count('id')).filter(total_orders__gt=1)

def get_total_sales_for_product(product_id):
    return OrderItem.objects.filter(product_id=product_id).aggregate(total_sales=Sum('price'))

def get_least_sold_items_for_vendor(vendor_id):
    order_items = OrderItem.objects.filter(product=OuterRef('pk')).values('product')
    total_sold = order_items.annotate(total=Sum('quantity')).values('total')
    least_sold_products = Product.objects.filter(vendor_id=vendor_id).annotate(total_sold=Coalesce(Subquery(total_sold), 0)).order_by('total_sold')
    
    result = []
    for least_sold_product in least_sold_products:
        if least_sold_product.total_sold == 0:   
            result.append({
                'id': least_sold_product.id,
                'title': least_sold_product.title,
                'total_sold': least_sold_product.total_sold,
            })
        else:
            break
    return result

def get_low_stock_products(threshold):
    return Product.objects.filter(amount_in_stock__lte=threshold)
