from django.urls import path
from .views import *
#API Endpoints for products
urlpatterns = [
    path('', ProductListView.as_view(), name="all_products"),#Lists all Products in the database
    
    path('categories/', CategoryListView.as_view(), name="all_categories"),#Lists all Categories in the database
    
    path('product/<int:id>/', ProductDetailView.as_view(), name='product_detail'),#Gets detail of a single product <int:id> should be product id(int)
    
    path('category/<str:category_slug>/', ProductsByCategoryView.as_view(), name='products_by_category'),#Gets products belonging to a particular category <str..> should be category slug(string)
    
    path('product/set-discount/', SetDiscountView.as_view(), name='set_discount'),#Allows venders to set discounts on products or a whole category of products. Only accepts post method, user must be authenticated/and must be a vendor
    
    path('product/terminate-discount/', TerminateDiscountView.as_view(), name='terminate_discount'),#Allows venders to set discounts on products or a whole category of products. Only accepts post method, user must be authenticated/and must be a vendor
    
    path('product/<int:product_id>/like/', ProductLikeView.as_view(), name='product-like'),#User like products
    
    path('product/<int:product_id>/unlike/', ProductDislikeView.as_view(), name='product-unlike'),#User unlike product
    
    path('user/recently-viewed/', RecentlyViewedListView.as_view(), name='recently-viewed'),#User recently viewed items
    
    path('product/comments/create/', ProductCommentCreateView.as_view(), name='create-comment'),#User create comments
    
    path('product/comments/list/<int:id>/', ProductCommentListView.as_view(), name='list-comment'),#List comments under a product, <int:id> is the product id
    
    path('product/comments/reply/create/', CommentReplyCreateView.as_view(), name='create-reply'),#User create comment reply
    
    path('product/comments/reply/list/<int:id>/', CommentReplyListView.as_view(), name='list-reply'),#List all comment replies under a comment, <in:id> is the comment id
    
    path('product/wishlist/<str:username>/', WishlistDetailView.as_view(), name='wishlist-detail'),#List products in wishlist for user
    
    path('product/wishlists/create/', WishlistCreateView.as_view(), name='wishlist-create'),#Create wishlist for user
    
    path('product/wishlists/remove/', WishlistRemoveView.as_view(), name='wishlist-remove'),#Create wishlist for user
    
    path('search/', SearchView.as_view(), name='search'),#Search For Products and Vendors
]
