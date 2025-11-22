# shop/context_processors.py
from .models import Cart

def cart_count(request):
    cart_items_count = 0

    if request.user.is_authenticated:
        # Logged-in user: count items from Cart model
        cart_items_count = Cart.objects.filter(user=request.user).count()
    else:
        # Guest user: count items from session
        cart = request.session.get('cart', {})
        for item in cart.values():
            cart_items_count += item.get('quantity', 0)

    return {
        'cart_items_count': cart_items_count
    }
