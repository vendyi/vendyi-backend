from django.urls import path
from .views import *
#API Endpoints for products
urlpatterns = [
    path('', ProductListView.as_view(), name="all_products"),#Lists all Products in the database
    
    path('categories/', CategoryListView.as_view(), name="all_categories"),#Lists all Categories in the database
    
    path('product/<int:id>/', ProductDetailView.as_view(), name='product_detail'),#Gets detail of a single product <int:id> should be product id(int)
    
    path('category/<str:category_slug>/', ProductsByCategoryView.as_view(), name='products_by_category'),#Gets products belonging to a particular category <str..> should be category slug(string)
]
