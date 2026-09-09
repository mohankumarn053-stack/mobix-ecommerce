from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Count
from .forms import SellerProductForm
from django.db.models import F
from .models import SellerOrder
from django.db.models import Sum
from .forms import (
    SellerProductForm,
    SellerApplicationForm,
    SellerStoreUpdateForm,
)
from .models import (
    Product,
    Category,
    Cart,
    CartItem,
    Order,
    SellerOrder,
    OrderItem,
    Wishlist,
    WishlistItem,
    SellerApplication,

)

def search_products(request):

    query = request.GET.get('q', '').strip()

    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(brand__icontains=query)
        )

    context = {
        'products': products,
        'query': query,
    }

    return render(
        request,
        'search_results.html',
        context
    )
def register(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check password match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        # Check username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        # Check email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('register')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Log the user in immediately
        login(request, user)

        return redirect('home')

    return render(request, 'register.html')

def user_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')

        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

            return redirect('login')

    return render(request, 'login.html')
def user_logout(request):

    logout(request)

    return redirect('home')

def home(request):
    categories = Category.objects.annotate(
        product_count=Count('products')
    )

    products = Product.objects.all().order_by('-created_at')[:8]

    context = {
        'categories': categories,
        'products': products,
    }

    return render(request, 'home.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    context = {
        'product': product,
    }

    return render(request, 'product_detail.html', context)

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if not request.user.is_authenticated:
        return redirect(
            f"/login/?next=/cart/add/{product.id}/"
        )

    if product.stock <= 0:
        return redirect(
            'product_detail',
            product_id=product.id
        )

    # Get quantity from product page
    quantity = int(
        request.POST.get('quantity', 1)
    )

    # Make sure quantity is at least 1
    if quantity < 1:
        quantity = 1

    # Don't allow more than available stock
    if quantity > product.stock:
        quantity = product.stock

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if created:

        cart_item.quantity = quantity
        cart_item.save()

    else:

        new_quantity = cart_item.quantity + quantity

        if new_quantity <= product.stock:
            cart_item.quantity = new_quantity
        else:
            cart_item.quantity = product.stock

        cart_item.save()

    return redirect('cart')
@login_required
def buy_now(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':

        quantity = int(
            request.POST.get('quantity', 1)
        )

    else:

        quantity = int(
            request.GET.get('quantity', 1)
        )

    if not request.user.is_authenticated:

        next_url = (
            f"/buy-now/{product.id}/"
            f"?quantity={quantity}"
        )

        return redirect(
            f"/login/?next={next_url}"
        )

    if quantity < 1:
        quantity = 1

    if quantity > product.stock:

        return redirect(
            'product_detail',
            product_id=product.id
        )

    request.session['buy_now'] = {
        'product_id': product.id,
        'quantity': quantity
    }

    return redirect('checkout')

@login_required
def cart(request):

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_items = cart.items.select_related('product')

    total = 0

    for item in cart_items:
        item.subtotal = (
            item.product.discounted_price * item.quantity
        )
        total += item.subtotal

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total': total,
    }

    return render(request, 'cart.html', context)


@login_required
def remove_from_cart(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    item.delete()

    return redirect('cart')

@login_required
def increase_quantity(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if item.quantity < item.product.stock:
        item.quantity += 1
        item.save()

    return redirect('cart')


@login_required
def decrease_quantity(request, item_id):

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')

@login_required
def checkout(request):

    buy_now_data = request.session.get('buy_now')

    # -----------------------------------
    # BUY NOW CHECKOUT
    # -----------------------------------

    if buy_now_data:

        product = get_object_or_404(
            Product,
            id=buy_now_data['product_id']
        )

        quantity = buy_now_data['quantity']

        # Check stock
        if quantity > product.stock:

            del request.session['buy_now']

            return redirect(
                'product_detail',
                product_id=product.id
            )

        subtotal = (
            product.discounted_price * quantity
        )

        checkout_items = [
            {
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal
            }
        ]

        total = subtotal

        checkout_type = 'buy_now'

    # -----------------------------------
    # NORMAL CART CHECKOUT
    # -----------------------------------

    else:

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_items = cart.items.select_related(
            'product'
        )

        if not cart_items.exists():

            return redirect('cart')

        checkout_items = []

        total = 0

        for item in cart_items:

            subtotal = (
                item.product.discounted_price
                * item.quantity
            )

            checkout_items.append({
                'product': item.product,
                'quantity': item.quantity,
                'subtotal': subtotal
            })

            total += subtotal

        checkout_type = 'cart'

   # -----------------------------------
    # PLACE ORDER
    # -----------------------------------

    if request.method == 'POST':

        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        payment_method = request.POST.get('payment_method')

        # -----------------------------------
        # BASIC VALIDATION
        # -----------------------------------

        if not all([
            full_name,
            phone,
            address,
            city,
            state,
            pincode,
            payment_method
        ]):

            context = {
                'checkout_items': checkout_items,
                'total': total,
                'error': 'Please fill in all the required fields.'
            }

            return render(
                request,
                'checkout.html',
                context
            )

        # -----------------------------------
        # CREATE ORDER
        # -----------------------------------

        with transaction.atomic():

            # -----------------------------------
            # CHECK STOCK AND SELLERS FIRST
            # -----------------------------------

            for item in checkout_items:

                product = item['product']
                quantity = item['quantity']

                # Product must have a seller
                if product.seller is None:

                    return render(
                        request,
                        'checkout.html',
                        {
                            'checkout_items': checkout_items,
                            'total': total,
                            'error': (
                                f'{product.name} does not have a seller '
                                f'assigned.'
                            )
                        }
                    )

                # Check stock again
                if quantity > product.stock:

                    return render(
                        request,
                        'checkout.html',
                        {
                            'checkout_items': checkout_items,
                            'total': total,
                            'error': (
                                f'Only {product.stock} units '
                                f'of {product.name} are available.'
                            )
                        }
                    )

            # -----------------------------------
            # CREATE MAIN CUSTOMER ORDER
            # -----------------------------------

            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                phone=phone,
                address=address,
                city=city,
                state=state,
                pincode=pincode,
                total_amount=total,
                payment_method=payment_method,
                status='Pending'
            )

            # -----------------------------------
            # CREATE SELLER ORDERS
            # -----------------------------------

            seller_orders = {}

            for item in checkout_items:

                product = item['product']
                quantity = item['quantity']
                subtotal = item['subtotal']

                seller = product.seller

                # -----------------------------------
                # CREATE SELLER ORDER IF NOT EXISTS
                # -----------------------------------

                if seller.id not in seller_orders:

                    seller_orders[seller.id] = SellerOrder.objects.create(
                        order=order,
                        seller=seller,
                        total_amount=0,
                        status='Pending'
                    )

                seller_order = seller_orders[seller.id]

                # -----------------------------------
                # CREATE ORDER ITEM
                # -----------------------------------

                OrderItem.objects.create(
                    order=order,
                    seller_order=seller_order,
                    product=product,
                    quantity=quantity,
                    price=product.discounted_price
                )

                # -----------------------------------
                # ADD TO SELLER TOTAL
                # -----------------------------------

                seller_order.total_amount += subtotal
                seller_order.save()

                # -----------------------------------
                # REDUCE STOCK
                # -----------------------------------

                product.stock -= quantity
                product.save()

            # -----------------------------------
            # CLEAR CART ONLY FOR NORMAL CHECKOUT
            # -----------------------------------

            if checkout_type == 'cart':

                cart.items.all().delete()

            # -----------------------------------
            # CLEAR BUY NOW SESSION
            # -----------------------------------

            if 'buy_now' in request.session:

                del request.session['buy_now']

        return redirect(
            'order_success',
            order_id=order.id
        )
    # -----------------------------------
    # CHECKOUT PAGE
    # -----------------------------------

    context = {
        'checkout_items': checkout_items,
        'total': total,
    }

    return render(
        request,
        'checkout.html',
        context
    )

@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'order_success.html',
        {
            'order': order
        }
    )

@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        'items__product'
    ).order_by('-created_at')

    context = {
        'orders': orders,
    }

    return render(
        request,
        'my_orders.html',
        context
    )

@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user
    )

    return render(
        request,
        'order_detail.html',
        {
            'order': order
        }
    )

@login_required
def my_account(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')

    wishlist = Wishlist.objects.filter(
        user=request.user
    ).first()

    wishlist_count = 0

    if wishlist:
        wishlist_count = wishlist.items.count()

    # ==========================================
    # SELLER APPLICATION STATUS
    # ==========================================

    seller_application = getattr(
        request.user,
        'seller_application',
        None
    )

    context = {
        'orders': orders,
        'wishlist_count': wishlist_count,
        'seller_application': seller_application,
    }

    return render(
        request,
        'my_account.html',
        context
    )
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # Guest user → Login first
    if not request.user.is_authenticated:
        return redirect(
            f'/login/?next=/wishlist/add/{product.id}/'
        )

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )

    WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )

    return redirect('wishlist')

@login_required
def wishlist(request):

    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user
    )

    wishlist_items = wishlist.items.select_related(
        'product'
    ).order_by('-added_at')

    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
    }

    return render(
        request,
        'wishlist.html',
        context
    )

@login_required
def remove_from_wishlist(request, item_id):

    item = get_object_or_404(
        WishlistItem,
        id=item_id,
        wishlist__user=request.user
    )

    item.delete()

    return redirect('wishlist')

def brand_products(request, brand_name):
    products = Product.objects.filter(
        brand__iexact=brand_name
    )

    return render(
        request,
        'brand_products.html',
        {
            'products': products,
            'brand': brand_name
        }
    )

@login_required
def seller_dashboard(request):

    # Only Sellers can access
    if not request.user.groups.filter(name='Seller').exists():
        return redirect('home')

    # ==========================================
    # SELLER'S PRODUCTS
    # ==========================================

    products = Product.objects.filter(
        seller=request.user
    ).order_by('-created_at')

    # ==========================================
    # SELLER'S ORDERS
    # ==========================================

    seller_orders = SellerOrder.objects.filter(
        seller=request.user
    ).select_related(
        'order'
    ).prefetch_related(
        'items__product'
    ).order_by(
        '-created_at'
    )

    # ==========================================
    # DASHBOARD STATISTICS
    # ==========================================

    total_products = products.count()

    active_products = products.filter(
        stock__gt=0
    ).count()

    total_orders = seller_orders.count()
    # =====================================================
    # SELLER SALES / EARNINGS
    # =====================================================

    # Completed orders
    delivered_orders = seller_orders.filter(
        status='Delivered'
    )

    # Total completed revenue
    total_sales = delivered_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # Number of completed orders
    completed_orders_count = delivered_orders.count()

    # Total quantity of products sold
    products_sold = OrderItem.objects.filter(
        seller_order__seller=request.user,
        seller_order__status='Delivered'
    ).aggregate(
        total=Sum('quantity')
    )['total'] or 0

    # ==========================================
    # CONTEXT
    # ==========================================

    context = {
        'products': products,
        'seller_orders': seller_orders,

        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'completed_orders_count': completed_orders_count,
        'products_sold': products_sold,
    }

    return render(
        request,
        'seller_dashboard.html',
        context
    )
@login_required
def seller_store(request):

    # ==========================================
    # CHECK SELLER ACCESS
    # ==========================================

    if not request.user.groups.filter(name='Seller').exists():
        messages.error(
            request,
            'You are not authorized to access the seller store.'
        )
        return redirect('home')

    # ==========================================
    # GET SELLER APPLICATION
    # ==========================================

    seller_application = SellerApplication.objects.filter(
        user=request.user,
        status='Approved'
    ).first()

    # ==========================================
    # NO APPROVED APPLICATION
    # ==========================================

    if not seller_application:
        messages.warning(
            request,
            'Your seller application could not be found or is not approved yet.'
        )
        return redirect('seller_dashboard')

    # ==========================================
    # GET SELLER PRODUCTS
    # ==========================================

    products = Product.objects.filter(
        seller=request.user
    ).order_by('-created_at')

    # ==========================================
    # CONTEXT
    # ==========================================

    context = {
        'seller_application': seller_application,
        'products': products,
    }

    return render(
        request,
        'seller_store.html',
        context
    )

@login_required
def seller_edit_store(request):

    # Only Sellers can access
    if not request.user.groups.filter(name='Seller').exists():
        return redirect('home')

    # Get approved seller application
    seller_application = get_object_or_404(
        SellerApplication,
        user=request.user,
        status='Approved'
    )

    if request.method == 'POST':

        form = SellerStoreUpdateForm(
            request.POST,
            instance=seller_application
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                'Your store information has been updated successfully.'
            )

            return redirect('seller_store')

    else:

        form = SellerStoreUpdateForm(
            instance=seller_application
        )

    return render(
        request,
        'seller_edit_store.html',
        {
            'form': form,
            'seller_application': seller_application,
        }
    )

   

@login_required
def seller_add_product(request):

    if not request.user.groups.filter(name='Seller').exists():
        return redirect('home')

    if request.method == 'POST':

        form = SellerProductForm(request.POST, request.FILES)

        if form.is_valid():

            product = form.save(commit=False)

            product.seller = request.user

            product.save()

            return redirect('seller_dashboard')

    else:

        form = SellerProductForm()

    return render(
        request,
        'seller_add_product.html',
        {
            'form': form
        }
    )

@login_required
def seller_edit_product(request, product_id):

    if not request.user.groups.filter(name='Seller').exists():
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id,
        seller=request.user
    )

    if request.method == 'POST':

        form = SellerProductForm(
            request.POST,
            request.FILES,
            instance=product
        )

        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')

    else:

        form = SellerProductForm(
            instance=product
        )

    return render(
        request,
        'seller_edit_product.html',
        {
            'form': form,
            'product': product
        }
    )

@login_required
def seller_delete_product(request, product_id):

    # Only Sellers can access
    if not request.user.groups.filter(name='Seller').exists():
        return redirect('home')

    # Seller can delete ONLY their own product
    product = get_object_or_404(
        Product,
        id=product_id,
        seller=request.user
    )

    # Only allow deletion through POST
    if request.method == 'POST':

        # Don't delete products that already have orders
        if OrderItem.objects.filter(product=product).exists():
            messages.error(
                request,
                'This product cannot be deleted because it has existing orders.'
            )
            return redirect('seller_dashboard')

        product.delete()

        messages.success(
            request,
            f'{product.name} was deleted successfully.'
        )

    return redirect('seller_dashboard')

@login_required
def seller_update_stock(request, product_id):

    if not request.user.groups.filter(name='Seller').exists():
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id,
        seller=request.user
    )

    if request.method == 'POST':

        stock = request.POST.get('stock')

        try:
            stock = int(stock)

            if stock < 0:
                messages.error(
                    request,
                    'Stock cannot be negative.'
                )
            else:
                product.stock = stock
                product.save()

                messages.success(
                    request,
                    f'Stock updated for {product.name}.'
                )

        except (TypeError, ValueError):
            messages.error(
                request,
                'Please enter a valid stock quantity.'
            )

    return redirect('seller_dashboard')

@login_required
def seller_update_order_status(request, order_id):

    # ==========================================
    # ONLY SELLERS CAN ACCESS
    # ==========================================

    if not request.user.groups.filter(name='Seller').exists():
        return redirect('home')


    # ==========================================
    # GET THIS SELLER'S ORDER
    # ==========================================

    seller_order = get_object_or_404(
        SellerOrder,
        order_id=order_id,
        seller=request.user
    )


    if request.method == 'POST':

        new_status = request.POST.get('status')


        # ==========================================
        # ALLOWED STATUSES
        # ==========================================

        allowed_statuses = [
            'Pending',
            'Confirmed',
            'Shipped',
            'Delivered',
            'Cancelled'
        ]


        if new_status not in allowed_statuses:

            messages.error(
                request,
                'Invalid order status.'
            )

            return redirect('seller_dashboard')


        # ==========================================
        # TERMINAL STATUS CHECK
        # ==========================================

        # Delivered and Cancelled are final.
        # They cannot be changed again.

        if seller_order.status in [
            'Delivered',
            'Cancelled'
        ]:

            messages.error(
                request,
                f'Order #{seller_order.order.id} is already '
                f'{seller_order.status} and cannot be changed.'
            )

            return redirect('seller_dashboard')


        # ==========================================
        # SHIPPED / DELIVERED CANNOT BE CANCELLED
        # ==========================================

        if (
            new_status == 'Cancelled'
            and seller_order.status in [
                'Shipped',
                'Delivered'
            ]
        ):

            messages.error(
                request,
                'This order cannot be cancelled because it has already been shipped.'
            )

            return redirect('seller_dashboard')


        # ==========================================
        # UPDATE EVERYTHING ATOMICALLY
        # ==========================================

        with transaction.atomic():


            # ======================================
            # RESTORE STOCK WHEN SELLER CANCELS
            # ======================================

            if new_status == 'Cancelled':

                for item in seller_order.items.select_related(
                    'product'
                ):

                    product = item.product

                    product.stock += item.quantity

                    product.save()


            # ======================================
            # UPDATE SELLER ORDER
            # ======================================

            seller_order.status = new_status

            seller_order.save()


            # ======================================
            # UPDATE ORDER ITEMS
            # ======================================

            seller_order.items.update(
                status=new_status
            )


            # ======================================
            # UPDATE MAIN CUSTOMER ORDER
            # ======================================

            order = seller_order.order


            seller_orders = order.seller_orders.all()


            statuses = list(
                seller_orders.values_list(
                    'status',
                    flat=True
                )
            )


            # ======================================
            # ALL CANCELLED
            # ======================================

            if all(
                status == 'Cancelled'
                for status in statuses
            ):

                order.status = 'Cancelled'


            # ======================================
            # ALL DELIVERED
            # ======================================

            elif all(
                status == 'Delivered'
                for status in statuses
            ):

                order.status = 'Delivered'


            # ======================================
            # ANY SHIPPED OR DELIVERED
            # ======================================

            elif any(
                status in [
                    'Shipped',
                    'Delivered'
                ]
                for status in statuses
            ):

                order.status = 'Shipped'


            # ======================================
            # ANY CONFIRMED
            # ======================================

            elif any(
                status == 'Confirmed'
                for status in statuses
            ):

                order.status = 'Confirmed'


            # ======================================
            # OTHERWISE PENDING
            # ======================================

            else:

                order.status = 'Pending'


            order.save()


        # ==========================================
        # SUCCESS MESSAGE
        # ==========================================

        if new_status == 'Cancelled':

            messages.success(
                request,
                f'Order #{order.id} cancelled successfully. '
                f'Product stock has been restored.'
            )

        else:

            messages.success(
                request,
                f'Order #{order.id} status updated to {new_status}.'
            )


    return redirect('seller_dashboard')
@login_required
def seller_order_detail(request, order_id):

    # ==========================================
    # ONLY SELLERS CAN ACCESS
    # ==========================================

    if not request.user.groups.filter(name='Seller').exists():
        return redirect('home')

    # ==========================================
    # GET ONLY THIS SELLER'S ORDER
    # ==========================================

    seller_order = get_object_or_404(
        SellerOrder.objects.select_related(
            'order',
            'seller'
        ).prefetch_related(
            'items__product'
        ),
        order_id=order_id,
        seller=request.user
    )

    # ==========================================
    # ORDER ITEMS BELONGING TO THIS SELLER
    # ==========================================

    order_items = seller_order.items.all()
    for item in order_items:
        item.subtotal = item.price * item.quantity

    context = {
        'seller_order': seller_order,
        'order': seller_order.order,
        'order_items': order_items,
    }

    return render(
        request,
        'seller_order_detail.html',
        context
    )

@login_required
def become_seller(request):

    # If already a seller, don't allow another application
    if request.user.groups.filter(name='Seller').exists():
        return redirect('seller_dashboard')

    # Check whether the user already has an application
    try:
        application = request.user.seller_application
    except SellerApplication.DoesNotExist:
        application = None

    if request.method == 'POST':

        if application:
            form = SellerApplicationForm(
                request.POST,
                instance=application
            )
        else:
            form = SellerApplicationForm(request.POST)

        if form.is_valid():

            seller_application = form.save(commit=False)

            # Automatically connect application to logged-in user
            seller_application.user = request.user

            # New/re-submitted application goes to Pending
            seller_application.status = 'Pending'

            seller_application.save()

            messages.success(
                request,
                'Your seller application has been submitted successfully. '
                'Please wait for admin approval.'
            )

            return redirect('my_account')

    else:

        if application:
            form = SellerApplicationForm(instance=application)
        else:
            form = SellerApplicationForm()

    return render(
        request,
        'become_seller.html',
        {
            'form': form,
            'application': application,
        }
    )

@login_required
def cancel_order(request, order_id):

    # Only allow POST requests
    if request.method != 'POST':
        return redirect('order_detail', order_id=order_id)

    # Get only the logged-in user's order
    order = get_object_or_404(
        Order.objects.prefetch_related(
            'seller_orders',
            'items__product'
        ),
        id=order_id,
        user=request.user
    )

    # -----------------------------------
    # CHECK CURRENT ORDER STATUS
    # -----------------------------------

    if order.status in ['Shipped', 'Delivered', 'Cancelled']:

        messages.error(
            request,
            f'Order #{order.id} cannot be cancelled because it is already {order.status}.'
        )

        return redirect(
            'order_detail',
            order_id=order.id
        )

    # -----------------------------------
    # GET SELLER ORDERS
    # -----------------------------------

    seller_orders = list(
        order.seller_orders.all()
    )

    # -----------------------------------
    # CHECK WHETHER ANY SELLER
    # HAS ALREADY SHIPPED THE ORDER
    # -----------------------------------

    non_cancellable_statuses = [
        'Shipped',
        'Delivered'
    ]

    for seller_order in seller_orders:

        if seller_order.status in non_cancellable_statuses:

            messages.error(
                request,
                'This order cannot be cancelled because one or more products have already been shipped.'
            )

            return redirect(
                'order_detail',
                order_id=order.id
            )

    # -----------------------------------
    # CANCEL EVERYTHING ATOMICALLY
    # -----------------------------------

    with transaction.atomic():

        # -----------------------------------
        # RESTORE PRODUCT STOCK
        # -----------------------------------

        for item in order.items.select_related('product'):

            product = item.product

            product.stock += item.quantity

            product.save()

        # -----------------------------------
        # CANCEL ORDER ITEMS
        # -----------------------------------

        order.items.update(
            status='Cancelled'
        )

        # -----------------------------------
        # CANCEL SELLER ORDERS
        # -----------------------------------

        for seller_order in seller_orders:

            seller_order.status = 'Cancelled'

            seller_order.save()

        # -----------------------------------
        # CANCEL MAIN CUSTOMER ORDER
        # -----------------------------------

        order.status = 'Cancelled'

        order.save()

    messages.success(
        request,
        f'Order #{order.id} has been cancelled successfully.'
    )

    return redirect(
        'order_detail',
        order_id=order.id
    )