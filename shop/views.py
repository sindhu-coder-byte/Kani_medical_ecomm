from django.shortcuts import render, get_object_or_404, redirect 
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import timedelta, date
from decimal import Decimal
from django.conf import settings
import os
import logging

from .models import Product, Cart, Category, Order
from .forms import SignupForm, LoginForm
import razorpay
from django.conf import settings



# Initialize logger
logger = logging.getLogger(__name__)

# -------------------------
# Home / Product Listing
# -------------------------
def home(request):
    hero_image = None
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, "image1.png")):
        hero_image = {"url": settings.MEDIA_URL + "image1.png"}

    cart_items_count = 0
    if request.user.is_authenticated:
        cart_items_count = Cart.objects.filter(user=request.user).count()
    else:
        cart = request.session.get('cart', {})
        for item in cart.values():
            cart_items_count += item.get('quantity', 0)

    context = {
        "hero_image": hero_image,
        "cart_items_count": cart_items_count
    }
    return render(request, "shop/home.html", context)

def about_page(request):
    return render(request, 'shop/about.html')

def contact_page(request):
    return render(request, 'shop/contact.html')
def contact_page(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        message = request.POST.get("message")
        agree_terms = request.POST.get("agree_terms")

        # Here you can save the message to the database if you have a model
        # Example:
        # Contact.objects.create(first_name=first_name, last_name=last_name, ...)

        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact_page")

    return render(request, "shop/contact.html")


# -------------------------
# Signup
# -------------------------
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if hasattr(user, 'set_password'):
                user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'shop/signup.html', {'form': form})


# -------------------------
# Login
# -------------------------
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'shop/login.html', {'form': form})


# -------------------------
# Logout
# -------------------------
def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('login')


# -------------------------
# Categories
# -------------------------
def categories(request):
    all_categories = Category.objects.all()
    all_products = Product.objects.all()
    context = {
        'categories': all_categories,
        'products': all_products,
    }
    return render(request, 'shop/categories.html', context)


# -------------------------
# Product Detail
# -------------------------
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    from_category = request.GET.get('from_category') == '1'

    context = {
        'product': product,
        'related_products': related_products,
        'from_category': from_category,
    }
    return render(request, 'shop/product_detail.html', context)


# -------------------------
# Add to Cart
# -------------------------
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} has been added to your cart!")
    return redirect('cart_page')


# -------------------------
# Cart Page
# -------------------------
from decimal import Decimal
import razorpay
from django.conf import settings

@login_required
def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = discount = total = Decimal('0.00')

    # Calculate subtotal, discount, total
    for item in cart_items:
        price = item.product.price
        final_price = item.product.final_price
        subtotal += Decimal(price) * item.quantity
        discount += (Decimal(price) - Decimal(final_price)) * item.quantity

    total = subtotal - discount

    # Razorpay minimum amount check
    total_amount = int(total * 100)
    if total_amount < 100:
        total_amount = 100  # Minimum ₹1 in paise

    # Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    razorpay_order = client.order.create({
        "amount": total_amount,
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'shop/cart.html', context)


# -------------------------
# Checkout Page (Dummy Payment)
# -------------------------
@login_required
def checkout_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    subtotal = discount = total = Decimal('0.00')

    # Calculate totals
    for item in cart_items:
        price = item.product.price
        final_price = item.product.final_price
        subtotal += Decimal(price) * item.quantity
        discount += (Decimal(price) - Decimal(final_price)) * item.quantity

    total = subtotal - discount

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        # Handle Razorpay payment verification
        if "razorpay_payment_id" in request.POST:
            razorpay_payment_id = request.POST.get("razorpay_payment_id")
            razorpay_order_id = request.POST.get("razorpay_order_id")
            razorpay_signature = request.POST.get("razorpay_signature")

            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }

            try:
                # Verify the payment signature
                client.utility.verify_payment_signature(params_dict)
                payment_status = "Paid"
                payment_method = "Paid Online"
            except razorpay.errors.SignatureVerificationError:
                messages.error(request, "Payment verification failed. Try again!")
                return redirect("cart_page")
        else:
            # Cash on Delivery
            payment_status = "Pending"
            payment_method = "Cash on Delivery"

        # Create order
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            payment_method=payment_method,
            payment_status=payment_status,
            total=total,
        )

        # Optionally, save cart items to order items
        # Clear the cart
        cart_items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect("order_success", order_id=order.id)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)

# -------------------------
# Order Success / Thank You Page
# -------------------------
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    tracked_order = None

    if request.method == "POST":
        email = request.POST.get("email")
        try:
            tracked_order = Order.objects.get(email=email)
        except Order.DoesNotExist:
            tracked_order = None

    return render(request, "shop/order_success.html", {
        "order": order,
        "tracked_order": tracked_order,
    })
    
def track_order(request, order_id):
    tracked_order = None
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            tracked_order = Order.objects.get(email=email)
            # Redirect to order_success with order_id
            return redirect('order_success', order_id=tracked_order.id)
        except Order.DoesNotExist:
            tracked_order = None
            # If you want to stay on the same page and show "No order found", you can render a template instead
            return render(request, 'shop/order_success.html', {
                "order": None,
                "tracked_order": None,
                "error": "No order found for this email."
            })
    return redirect('home')


