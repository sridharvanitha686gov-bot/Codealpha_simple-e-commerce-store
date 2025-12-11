from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Order
from .forms import RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
def home(request):
    products = Product.objects.all()
    return render(request, 'store/home.html', {'products': products})
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/product_detail.html', {'product': product})
def _get_cart(request):
    return request.session.setdefault('cart', {})
def cart_view(request):
    cart = _get_cart(request)
    items = []
    total = 0
    for pid, qty in cart.items():
        try:
            p = Product.objects.get(pk=int(pid))
        except Product.DoesNotExist:
            continue
        subtotal = p.price * qty
        items.append({'product': p, 'quantity': qty, 'subtotal': subtotal})
        total += subtotal
    return render(request, 'store/cart.html', {'items': items, 'total': total})
def cart_add(request, product_id):
    cart = _get_cart(request)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session.modified = True
    return redirect('cart')
def cart_remove(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
    return redirect('cart')
@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.info(request, 'Your cart is empty.')
        return redirect('home')
    total = 0
    for pid, qty in cart.items():
        p = Product.objects.get(pk=int(pid))
        total += p.price * qty
    order = Order.objects.create(user=request.user, total=total)
    request.session['cart'] = {}
    return render(request, 'store/order_confirmation.html', {'order': order})
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user); return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'store/login.html')
def user_logout(request):
    logout(request); return redirect('home')
