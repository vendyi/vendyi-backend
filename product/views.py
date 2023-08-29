from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.response import Response
from .models import Product, Category
from .serializers import ProductListSerializer, ProductCategorySerializer, ProductDetailSerializer, CategorySerializer

class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Products"})
        else:
            return self.list(request, *args, **kwargs)
        
class ProductsByCategoryView(generics.ListAPIView):
    serializer_class = ProductCategorySerializer

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        try:
            category = Category.objects.get(slug=category_slug)
            queryset = Product.objects.filter(category=category)
            return queryset
        except Category.DoesNotExist:
            return Product.objects.none()  # Return an empty queryset
        
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if len(queryset) == 0:
            return Response({"message": "No Products in the category"})
        else:
            return super().list(request, *args, **kwargs)
        

class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = 'id'
    def get_queryset(self):
        queryset = Product.objects.all()
        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "This product does not exist"}, status=404)
        else:
            return self.retrieve(request, *args, **kwargs)

class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No Products"})
        else:
            return self.list(request, *args, **kwargs)