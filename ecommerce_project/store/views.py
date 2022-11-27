from dataclasses import fields


from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from store.models import Product
import json
import datetime

from .utils import cookieCart, cartData, guestOrder


class CustomLoginView(LoginView):
    template_name = "store/login.html"
    fields = "__all__"
    redirect_authenticated_user: True

    def get_success_url(self):
        return reverse("home")
        # return reverse("store", args=[self.request.user.id])


def HomePage(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(complete=False)

    else:
        orders = {"get_cart_total": 0, "get_cart_item": 0, "shipping": False}
    cartitem = 0
    # cartitem = orders.get_cart_item
    # avoid an error if cart cookie when loads first time by user
    try:
        cart = json.loads(request.COOKIES["cart"])
    except:
        cart = {}
    print("cart:", cart)

    for i in cart:
        cartitem += cart[i]["quantity"]
    customer = Customer.objects.all()
    context = {"orders": orders, "customer": customer, "cartitem": cartitem}
    return render(request, "store/home.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print("Action:", action)
    print("productId:", productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity = orderItem.quantity + 1
    elif action == "remove":
        orderItem.quantity = orderItem.quantity - 1
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


class ProductList(ListView):
    model = Product
    template_name = "store/store.html"
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        print(self.request.user)
        context = super().get_context_data(**kwargs)
        context["orders"] = Order.objects.filter(complete=False)

        return context


class OrderList(LoginRequiredMixin, ListView):
    model = OrderItem
    template_name = "store/cart.html"
    context_object_name = "items"

    def get_queryset(self):
        return OrderItem.objects.filter(
            order=Order.objects.get(id=self.kwargs["pk"], complete=False)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order_1"] = Order.objects.get(id=self.kwargs["pk"], complete=False)
        context["orders"] = Order.objects.filter(complete=False)
        return context


def store(request):
    # data = cartData(request)

    # cartItems = data["cartItems"]
    # order = data["order"]
    # items = data["items"]
    order = {"get_cart_total": 0, "get_cart_item": 0, "shipping": False}
    cartitem = order["get_cart_item"]
    try:
        cart = json.loads(request.COOKIES["cart"])
    except:
        cart = {}
    print("Cart:", cart)

    for i in cart:
        cartitem += cart[i]["quantity"]

    products = Product.objects.all()
    context = {"products": products, "cartitem": cartitem}
    return render(request, "store/store.html", context)


def cart(request):
    cookieData = cookieCart(request)
    cartitem = cookieData["cartitem"]
    order_1 = cookieData["order"]
    items = cookieData["items"]

    return render(
        request,
        "store/cart.html",
        {
            "cartitem": cartitem,
            "order_1": order_1,
            "items": items,
        },
    )


def checkoutPage(request):
    if request.user.is_authenticated:
        orders = Order.objects.filter(complete=False)
        customer = request.user.customer
        print(request.user)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        product = Product.objects.all()
        items = order.orderitem_set.all()
    else:

        cookieData = cookieCart(request)
        cartitem = cookieData["cartitem"]
        order = cookieData["order"]
        # orders = cookieData["order"]
        items = cookieData["items"]

    context = {
        "items": items,
        "order": order,
        # "orders": orders,
        # "cartitem": cartitem,
    }
    return render(request, "store/checkout.html", context)


def processOrder(request):
    data = json.loads(request.body)
    # print("Data:", request.body)
    transaction_id = datetime.datetime.now().timestamp()

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data["form"]["total"])
    order.transaction_id = transaction_id

    # avoid manipulating by user
    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )

    return JsonResponse("Payment submitted..", safe=False)
