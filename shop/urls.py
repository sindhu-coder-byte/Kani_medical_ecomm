from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_page, name='About'),
    path('contact/', views.contact_page, name='Contact'),
    path('contact/submit/', views.contact_page, name='contact_submit'),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Cart
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_page, name='cart_page'),

    # Checkout
    path('checkout/', views.checkout_page, name='checkout_page'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # Order Tracking
    path('track/<int:order_id>/', views.track_order, name='track_order'),

    # Products
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # Categories
    path('categories/', views.categories, name='categories'),
]

# Serve media files even when DEBUG = False (Render deploy)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
