from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

# ----------------- Category -----------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# ----------------- Product -----------------
class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')

    stock = models.PositiveIntegerField(default=0)

    # Ratings
    rating = models.PositiveIntegerField(default=0)
    rating_count = models.PositiveIntegerField(default=0)

    # Extra features
    is_featured = models.BooleanField(default=False)
    badge = models.CharField(max_length=50, blank=True, null=True)
    key_benefits = models.TextField(blank=True, null=True, help_text="Enter one benefit per line")

    def __str__(self):
        return self.name

    # --------- Properties for template ---------
    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def offer(self):
        """Returns the discount percentage as a string, or None if no discount."""
        if self.discount_price and self.price and self.discount_price < self.price:
            discount_percent = int((self.price - self.discount_price) / self.price * 100)
            return f"{discount_percent}%"
        return None

    @property
    def final_price(self):
        """Returns the price that should be displayed (discounted if available)."""
        return self.discount_price if self.discount_price else self.price


# ----------------- Product Images -----------------
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')

    def __str__(self):
        return f"{self.product.name} Image"


# ----------------- User Uploaded Images -----------------
class ProductUserImage(models.Model):
    product = models.ForeignKey(Product, related_name='user_images', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/user_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} User Image"


# ----------------- Key Benefits -----------------
class ProductBenefit(models.Model):
    product = models.ForeignKey(Product, related_name='benefits', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product.name} - {self.title}"


# ----------------- Reviews -----------------
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})"


# ----------------- Cart -----------------
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_products")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.user.username})"

    @property
    def total_price(self):
        """Total price for this cart item (considering discount if available)."""
        return self.quantity * self.product.final_price


# ----------------- Product Thumbnail -----------------
class ProductThumbnail(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='thumbnails')
    image = models.ImageField(upload_to='products/thumbnails/')

    def __str__(self):
        return f"{self.product.name} Thumbnail"


# ----------------- Order -----------------
ORDER_STATUS = [
    ('placed', 'Placed'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled'),
]

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    # Customer info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    # Order info
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    order_items = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='placed')
    payment_method = models.CharField(max_length=50, default="COD")
    payment_status = models.CharField(max_length=20, default="Pending")

    # Razorpay
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.email} ({self.payment_status})"


# ----------------- Order Item -----------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# ----------------- Cart Item -----------------
class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} in cart"
