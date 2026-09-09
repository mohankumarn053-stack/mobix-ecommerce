from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    Category,
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Wishlist,
    WishlistItem,
    SellerApplication,
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'brand',
        'seller',
        'category',
        'price',
        'discount',
        'stock',
        'rating',
        'created_at',
    )

    list_filter = (
        'brand',
        'category',
        'discount',
    )

    search_fields = (
        'name',
        'brand',
        'description',
    )

    ordering = (
        '-created_at',
    )
    list_per_page = 20
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'full_name',
        'total_amount',
        'payment_method',
        'status',
        'created_at'
    )

    list_filter = ('status', 'payment_method')
    search_fields = (
        'full_name',
        'phone',
        'city',
        'state',
        'pincode',
        'user__username',
        'user__email',
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'created_at'
    )

    search_fields = (
        'user__username',
        'user__email'
    )


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'wishlist',
        'product',
        'added_at'
    )

    search_fields = (
        'product__name',
        'wishlist__user__username'
    )

@admin.register(SellerApplication)
class SellerApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'store_name',
        'full_name',
        'user_username',
        'user_email',
        'phone',
        'seller_type',
        'state',
        'status',
        'created_at',
        'reviewed_at',
    )

    list_filter = (
        'status',
        'seller_type',
        'state',
    )

    search_fields = (
        'store_name',
        'full_name',
        'user__username',
        'user__email',
        'phone',
        'city',
    )

    ordering = (
        '-created_at',
    )

    list_per_page = 20

    def user_username(self, obj):
        return obj.user.username

    user_username.short_description = 'Username'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'

    def save_model(self, request, obj, form, change):

        # Save the application first
        super().save_model(request, obj, form, change)

        # Get or create Seller group
        seller_group, created = Group.objects.get_or_create(
            name='Seller'
        )

        # =========================
        # APPROVED
        # =========================

        if obj.status == 'Approved':

            # Add user to Seller group
            obj.user.groups.add(seller_group)

            # Save user
            obj.user.save()

            # Set reviewed time
            if obj.reviewed_at is None:
                from django.utils import timezone

                obj.reviewed_at = timezone.now()
                obj.save(update_fields=['reviewed_at'])

        # =========================
        # REJECTED
        # =========================

        elif obj.status == 'Rejected':

            # Remove Seller access
            obj.user.groups.remove(seller_group)

            obj.user.save()

            if obj.reviewed_at is None:
                from django.utils import timezone

                obj.reviewed_at = timezone.now()
                obj.save(update_fields=['reviewed_at'])

        # =========================
        # PENDING
        # =========================

        elif obj.status == 'Pending':

            # Keep user as normal user
            obj.user.groups.remove(seller_group)

            obj.user.save()
