from django.urls import path
from .views import item_list, ItemDetailView, ItemSearchView, add_review, CartView, add_to_cart, CartManagementView, \
    EmptyCartView, CustomerRegistrationView, CheckoutView, CustomerLoginView, CustomerLogoutView, CustomerProfileView, \
    CustomerOrderDetailView, ItemListView

app_name = 'main'
urlpatterns = [
    path('', item_list, name='item_list'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart-management/<int:ci_id>/', CartManagementView.as_view(), name='cart-management'),
    path('empty-cart/', EmptyCartView.as_view(), name='emptycart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('login/', CustomerLoginView.as_view(), name='login'),
    path('logout/', CustomerLogoutView.as_view(), name='logout'),
    path('register/', CustomerRegistrationView.as_view(), name='register'),
    path('profile/', CustomerProfileView.as_view(), name='profile'),
    path('profile/order-<int:pk>/', CustomerOrderDetailView.as_view(), name='customerorderdetail'),
    path('<slug:category_slug>/', item_list, name='item_list_by_category'),
    path('items/<slug:slug>/', ItemDetailView.as_view(), name='item_detail'),
    path('add-review/<slug:slug>/', add_review, name='add_review'),
    path('add-to-cart/<int:pk>/', add_to_cart, name='add-to-cart'),
    path('search', ItemSearchView.as_view(), name='search'),
]