from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)

    description = models.TextField()

    image = models.ImageField(upload_to='products/')

    storage = models.CharField(max_length=50, blank=True)
    ram = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True)
    display = models.CharField(max_length=100, blank=True)
    processor = models.CharField(max_length=100, blank=True)
    camera = models.CharField(max_length=100, blank=True)
    battery = models.CharField(max_length=100, blank=True)

    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def discounted_price(self):
        return self.price - (self.price * self.discount / 100)

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, default='Cash on Delivery')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
class SellerOrder(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='seller_orders'
    )

    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seller_orders'
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.order.id} - {self.seller.username}"

class OrderItem(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    seller_order = models.ForeignKey(
        SellerOrder,
        on_delete=models.CASCADE,
        related_name='items',
        null=True,
        blank=True
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
class Wishlist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username}'s Wishlist"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['wishlist', 'product'],
                name='unique_wishlist_product'
            )
        ]

    def __str__(self):
        return f"{self.product.name} - {self.wishlist.user.username}"

class SellerApplication(models.Model):

    SELLER_TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Retailer', 'Retailer'),
        ('Manufacturer', 'Manufacturer'),
        ('Distributor', 'Distributor'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='seller_application'
    )

    full_name = models.CharField(
        max_length=200
    )

    store_name = models.CharField(
        max_length=200
    )

    phone = models.CharField(
        max_length=20
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    seller_type = models.CharField(
        max_length=30,
        choices=SELLER_TYPE_CHOICES
    )

    products_to_sell = models.CharField(
        max_length=300
    )

    description = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.store_name} - {self.user.username}"
