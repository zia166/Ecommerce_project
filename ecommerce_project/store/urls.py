from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("", views.HomePage, name="home"),
    path("store/<int:pk>", views.ProductList.as_view(), name="store"),
    path("store/", views.store, name="store1"),
    path("cart/<int:pk>/", views.OrderList.as_view(), name="cart"),
    path("cart/", views.cart, name="cart1"),
    # path("Create/<int:pk>/", views.OrderCreateView.as_view(), name="create"),
    path("update_item/", views.updateItem, name="update_item"),
    path("checkout/", views.checkoutPage, name="checkout"),
    path("process-order/", views.processOrder, name="process-order"),
]
