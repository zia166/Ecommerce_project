from dataclasses import fields

from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView

from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from store.models import Product


class CustomLoginView(LoginView):
    template_name = "store/login.html"
    fields = "__all__"
    redirect_authenticated_user: True

    def get_success_url(self):

        return reverse("store", args=[self.request.user.id])


def HomePage(request):
    orders = Order.objects.all()
    customer = Customer.objects.all()
    context = {"orders": orders, "customer": customer}
    return render(request, "store/home.html", context)


def CustomerPage(request, pk):
    orders = Order.objects.get(customer_id=pk)
    customer = Customer.objects.all()
    context = {"orders": orders, "customer": customer}
    return render(request, "store/home.html", context)


class ProductList(ListView):
    model = Product
    template_name = "store/store.html"
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["order"] = Order.objects.get(id=self.kwargs["pk"])
        context["order"] = Order.objects.all()

        return context


# def cart(request):

#     if request.user.is_authenticated:

#         customer = request.user.customer
#         print(request.user)
#         order, created = Order.objects.get_or_create(customer=customer, complete=False)

#         items = order.orderitem_set.all()
#         print(items)
#     else:
#     Create empty cart for now for non-logged in user
#     items = []

#     context = {"items": items, "order": order}
#     return render(request, "store/cart.html", context)


class OrderList(LoginRequiredMixin, ListView):
    model = OrderItem
    template_name = "store/cart.html"
    context_object_name = "items"

    def get_queryset(self):

        return OrderItem.objects.filter(order=Order.objects.get(id=self.kwargs["pk"]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = Order.objects.get(id=self.kwargs["pk"])
        return context


# class OrderCreate(LoginRequiredMixin, CreateView):
#     template_name = "order_form.html"
#     form_class = OrderForm
#     other_form_class = OrderListForm
#     # success_url: reverse_lazy("store")

#     def get_context_data(self, *args, **kwargs):
#         context_data = super(OrderCreate, self).get_context_data(*args, **kwargs)

#         context_data.update(
#             {
#                 "new_customer": True,
#                 "other_form": other_form_class,
#             }
#         )
#         return context_data


# class OrderItemCreate(LoginRequiredMixin, CreateView):
#     model = OrderItem
#     fields = "__all__"
#     template_name = "order_form.html"
#     success_url: reverse_lazy("store")

#     def form_valid(self, form):
#         form.instance.created_by = self.request.user
#         return super().form_valid(form)


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = OrderItem
    fields = ["product", "quantity", "order"]

    template_name = "store/order_form.html"
    # success_url: reverse_lazy("store")
    def get_initial(self):
        initial_data = super(OrderCreateView, self).get_initial()
        order = Order.objects.get(id=self.kwargs["pk"])
        initial_data["order"] = order
        return initial_data

    # def form_valid(self, form):
    #     form.instance.user = self.request.user
    #     form["order"].field.widget.attr["readonly"] = "readonly"
    #     return super(OrderCreateView, self).form_valid(form)

    def get_success_url(self):

        return reverse("store", args=[self.request.user.id])
