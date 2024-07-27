from django.urls import path
from .import views
import uuid


urlpatterns = [
    path('',views.index,name='index'),
    path('cctv_cameras/',views.cameras,name='cameras'),
    path('accessories/',views.Accessories,name='accessories'),
    path('update_quantity/', views.update_quantity, name='update_quantity'),
    path('products/',views.all_products,name='products'),
    path('products/<uuid:product_id>/',views.viewProduct,name='add_item'),
    path('updateCart/',views.updateCart,name='updateCart'),
    path('process_order/',views.processorder,name='processorder'),
    path('accesscontrol/',views.accesscontrol,name='accesscontrol'),
    path('fence/',views.fence,name='fence'),
    path('contact_us/',views.customer_feedback,name='feedback'),
    path('subscribe/',views.newsletter_emails,name='subscribe'),
    path('intercom/',views.intercom,name='intercom'),
    path('alarm/',views.alarms,name='alarms'),
    path('automatic_gates/',views.gates,name='gates'),
    path('cart/',views.cart,name='cart'),
    path('orders/',views.complete_orders,name='orders'),
    path('orders/<uuid:order_id>/',views.complete_orders_items,name='order_item'),
    path('checkout/',views.checkout,name='checkout'),
    path('login/',views.login_user,name='login'),
    path('register/',views.signup_user,name='register'),
    path('search_results/',views.search_products,name='search_product'),
    path('logout/',views.logout_user_profile,name='logout'),
    path('user_profile/<uuid:customer_id>/',views.user_profile,name='update_profile'),
    path('user_profile/',views.new_profile,name='profile'),
  
]