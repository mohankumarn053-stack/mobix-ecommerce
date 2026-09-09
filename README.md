# 📱 MOBIX — Smartphone E-Commerce Platform

> A full-stack multi-vendor smartphone e-commerce platform built with **Django, MySQL, HTML, CSS, and JavaScript**.

MOBIX provides a complete online shopping experience for customers while also supporting a multi-vendor seller system where sellers can manage their stores, products, inventory, and customer orders.

---

## 🚀 Project Overview

MOBIX is designed as a modern smartphone marketplace that provides separate experiences for **customers and sellers**.

Customers can browse and purchase smartphones, manage their cart and wishlist, place orders, and track their order status.

Sellers can create and manage their stores, add and manage products, update stock, and process customer orders.

---

## ✨ Key Features

### 👤 Customer Features

- User registration and login
- User authentication
- Browse smartphones
- Search products
- Browse products by brand
- View detailed product information
- Add products to cart
- Manage cart quantities
- Add products to wishlist
- Checkout
- Cash on Delivery
- Place orders
- View order history
- View order details
- Track order status
- Cancel eligible orders
- Manage account information

### 🏪 Seller Features

- Become a Seller application
- Seller dashboard
- Seller store management
- Add products
- Edit products
- Delete products
- Update product stock
- Manage store information
- View customer orders
- Update order status
- View detailed order information

### 📦 Order Management

Customers can track their orders through different stages:

```text
Order Placed
     ↓
Confirmed
     ↓
Shipped
     ↓
Delivered
```

Eligible orders can also be cancelled by the customer.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend programming |
| Django | Web framework and application logic |
| MySQL | Relational database |
| HTML5 | Page structure |
| CSS3 | Styling and responsive UI |
| JavaScript | Frontend interactions |
| Bootstrap Icons | UI icons |
| Git | Version control |
| GitHub | Source code management |

---

## 🔄 Application Workflow

```text
                         MOBIX
                           │
             ┌─────────────┴─────────────┐
             │                           │
          Customer                     Seller
             │                           │
       Register/Login             Become a Seller
             │                           │
      Browse Products             Seller Dashboard
             │                           │
      Search / Brands             Manage Store
             │                           │
      Product Details             Manage Products
             │                           │
      Cart / Wishlist             Manage Stock
             │                           │
         Checkout                Manage Orders
             │                           │
       Place Order             Update Order Status
             │
        Track Order
             │
     Cancel Eligible Order
```

---

## 📦 Order Workflow

```text
Customer
    │
    ▼
Browse Smartphones
    │
    ▼
View Product
    │
    ▼
Add to Cart
    │
    ▼
Checkout
    │
    ▼
Place Order
    │
    ▼
Order Placed
    │
    ▼
Confirmed
    │
    ▼
Shipped
    │
    ▼
Delivered
```

---

## 📁 Project Structure

```text
mobix-ecommerce/
│
├── ecommerce/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── store/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── products.html
│   ├── product_detail.html
│   ├── brand_products.html
│   ├── search_results.html
│   ├── cart.html
│   ├── checkout.html
│   ├── wishlist.html
│   ├── my_orders.html
│   ├── order_detail.html
│   ├── order_success.html
│   ├── my_account.html
│   ├── login.html
│   ├── register.html
│   ├── become_seller.html
│   ├── seller_dashboard.html
│   ├── seller_store.html
│   ├── seller_add_product.html
│   ├── seller_edit_product.html
│   ├── seller_edit_store.html
│   └── seller_order_detail.html
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── seller.css
│   │   └── become_seller.css
│   │
│   └── js/
│       └── scripts.js
│
├── media/
│   └── products/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sansanju5413/mobix-ecommerce.git
cd mobix-ecommerce
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root directory.

```env
SECRET_KEY=your-django-secret-key

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=3306
```

> **Important:** Never commit your `.env` file or database credentials to GitHub.

---

## 🗄️ Database Setup

Create the MySQL database:

```sql
CREATE DATABASE mobile_ecommerce;
```

Configure your database credentials in the `.env` file.

Run Django migrations:

```bash
python manage.py migrate
```

---

## ▶️ Run the Application

Start the Django development server:

```bash
python manage.py runserver
```

Open the application in your browser:

```text
http://127.0.0.1:8000/
```

---

## 💳 Payment Method

The current version supports:

- **Cash on Delivery**

Online payment gateway integration is planned as a future enhancement.

---

## 📸 Screenshots

Screenshots of the MOBIX customer and seller interfaces will be added here.

Future versions of this section will showcase:

- Home page
- Product listing
- Product details
- Shopping cart
- Checkout
- Customer account
- Order tracking
- Seller dashboard
- Seller store
- Product management
- Order management

---

## 🔮 Future Improvements

- Online payment gateway integration
- Production deployment
- PostgreSQL production database
- Product reviews and ratings
- Advanced product filtering
- Order notifications
- Email notifications
- Seller analytics
- Customer recommendations
- Improved admin analytics
- Cloud media storage
- Production security configuration

---

## 🌐 Project Status

**Status: Development Version**

The core customer shopping workflow and seller management functionality have been implemented and tested locally.

The project is currently being prepared for production deployment.

---

## 👨‍💻 Author

### Mohan Kumar N

Full-Stack Developer | Django | Python | MySQL

**GitHub:**  
https://github.com/mohankumarn053-stack

**Project Repository:**  
https://github.com/sansanju5413/mobix-ecommerce

---

## 📄 License

This project was developed as a personal portfolio and learning project.
