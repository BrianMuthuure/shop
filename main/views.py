from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy

from .forms import CommentForm, CustomerRegistrationForm, CustomerLoginForm, CheckoutForm
from .models import Item, Category, Review, Cart, CartItem, Customer, Order

from django.core.paginator import Paginator
from django.db.models import Avg
from django.views.generic import ListView, DetailView, TemplateView, CreateView, View, FormView


class CustomerMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()
        return super(CustomerMixin, self).dispatch(request, *args, **kwargs)


def item_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    items = Item.objects.filter(active=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        items = items.filter(category=category)
    context = {

        'category': category,
        'categories': categories,
        'items': items
    }
    return render(request, 'items/item_list.html', context)


class ItemListView(CustomerMixin, ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'home.html'


class ItemDetailView(CustomerMixin, DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'items/item_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        results = Review.objects.filter(item=self.object)
        context['reviews'] = Review.objects.filter(item=self.object)
        average = results.aggregate(Avg("rate"))['rate__avg']
        if average is None:
            average = 0
        else:
            average = round(average, 2)
        context['average'] = average
        return context


class ItemSearchView(ListView):
    model = Item
    template_name = 'items/search.html'

    def get_context_data(self, **kwargs):
        context = super(ItemSearchView, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        items = Item.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        context['items'] = items
        return context


def add_review(request, slug):
    if request.user.is_authenticated:
        item = Item.objects.get(slug=slug)
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.comment = request.POST['comment']
                data.rate = request.POST['rate']
                data.user = request.user
                data.item = item
                data.save()
                return redirect("main:item_detail", slug)
        else:
            form = CommentForm()
        return render(request, 'items/item_detail.html', {'form': form})
    else:
        return redirect("main:item_list")


class CartView(CustomerMixin, TemplateView):
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super(CartView, self).get_context_data(**kwargs)
        cart_id = self.request.session.get('cart_id', None)
        print(cart_id)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


def add_to_cart(request, pk):
    item_obj = get_object_or_404(Item, id=pk)
    cart_id = request.session.get('cart_id', None)
    print(cart_id)
    if cart_id:
        cart_obj = Cart.objects.get(id=cart_id)
        item_qs = cart_obj.cartitem_set.filter(item=item_obj)
        if item_qs.exists():
            cartitem = item_qs.last()
            cartitem.quantity += 1
            cartitem.subtotal += item_obj.selling_price
            cartitem.save()
            cart_obj.total += item_obj.selling_price
            cart_obj.save()
            return redirect('main:cart')
        else:
            cartitem = CartItem.objects.create(
                cart=cart_obj,
                item=item_obj,
                rate=item_obj.selling_price,
                quantity=1,
                subtotal=item_obj.selling_price
            )
            cart_obj.total += item_obj.selling_price
            cart_obj.save()
            return redirect('main:cart')
    else:
        cart_obj = Cart.objects.create(total=0)
        request.session['cart_id'] = cart_obj.id
        cartitem = CartItem.objects.create(
            cart=cart_obj, item=item_obj, rate=item_obj.selling_price, quantity=1, subtotal=item_obj.selling_price
        )
        cart_obj.total += item_obj.selling_price
        cart_obj.save()

        print(cart_id)
        return redirect('main:cart')


class CartManagementView(CustomerMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        ci_id = kwargs['ci_id']
        action = request.GET.get("action")
        ci_obj = CartItem.objects.get(id=ci_id)
        cart_obj = ci_obj.cart
        if action == 'increase':
            ci_obj.quantity += 1
            ci_obj.subtotal += ci_obj.rate
            ci_obj.save()
            cart_obj.total += ci_obj.rate
            cart_obj.save()
        elif action == 'decrease':
            ci_obj.quantity -= 1
            ci_obj.subtotal -= ci_obj.rate
            ci_obj.save()
            cart_obj.total -= ci_obj.rate
            cart_obj.save()
            if ci_obj.quantity == 0:
                ci_obj.delete()
        elif action == 'remove':
            cart_obj.total -= ci_obj.subtotal
            cart_obj.save()
            ci_obj.delete()
        else:
            pass
        return redirect('main:cart')


class EmptyCartView(CustomerMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartitem_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect('main:cart')


class CustomerRegistrationView(CustomerMixin, CreateView):
    template_name = 'registration.html'
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('main:item_list')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password2')
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,

        )
        form.instance.user = user
        return super(CustomerRegistrationView, self).form_valid(form)


class CheckoutView(CustomerMixin, CreateView):
    template_name = 'cart/checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy("main:item_list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect('/login/?next=/checkout/')
        return super(CheckoutView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CheckoutView, self).get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        user = self.request.user
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.created_by = f"{user.first_name} {user.last_name}"
            form.instance.total = cart_obj.total
            form.instance.status = 'Received'
            del self.request.session['cart_id']  # Delete the session after the order is complete
        else:
            return redirect("main:item_list")
        return super(CheckoutView, self).form_valid(form)


class CustomerLoginView(FormView):
    template_name = 'login.html'
    form_class = CustomerLoginForm
    success_url = reverse_lazy('main:item_list')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        usr = authenticate(username=username, password=password)
        if usr is not None and Customer.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {'form': self.form_class, "error": "Invalid credentials"})
        return super(CustomerLoginView, self).form_valid(form)

    def get_success_url(self):
        if "next" in self.request.GET:
            next_url = self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class CustomerLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('main:item_list')


class CustomerProfileView(TemplateView):
    template_name = 'customer/customer_profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect('/login/?next=/profile/')
        return super(CustomerProfileView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        customer = self.request.user.customer
        context = super(CustomerProfileView, self).get_context_data(**kwargs)
        context['customer'] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context['orders'] = orders
        return context


class CustomerOrderDetailView(DetailView):
    template_name = 'customer/order_detail.html'
    model = Order
    context_object_name = 'ord_obj'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs['pk']
            print(order_id)
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect('ecommerce:profile')

        else:
            return redirect('/login/?next=/profile/')
        return super(CustomerOrderDetailView, self).dispatch(request, *args, **kwargs)