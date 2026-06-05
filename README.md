# 🛒 Django E-Commerce REST API

A full-featured e-commerce backend built with **Django** and **Django REST Framework**, featuring JWT authentication, Stripe payment integration, inventory management, and a complete order lifecycle.

---

## ✨ Features

- **User Authentication** — Custom user model with email-based login and JWT tokens via Simple JWT
- **Product Catalog** — Full CRUD for products and categories, with an EAV (Entity-Attribute-Value) system for flexible product specifications
- **Shopping Cart** — Per-user persistent cart with add, update, remove, clear, and sync operations
- **Order Management** — Draft → Pending Payment → Paid → Shipped → Delivered order lifecycle with address snapshotting
- **Stripe Payments** — Checkout session creation, webhook handling, and automatic order fulfillment
- **Inventory Control** — Two-field stock model (`quantity_on_hand` / `quantity_available`) with atomic reservations to prevent overselling
- **Product Reviews** — Purchase-verified reviews with admin moderation queue
- **API Documentation** — Auto-generated Swagger UI via drf-spectacular

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0, Django REST Framework 3.16 |
| Authentication | Simple JWT |
| Payments | Stripe |
| Database | SQLite (dev) |
| API Docs | drf-spectacular / Swagger UI |
| Media Storage | Local filesystem (dev) |

---

## 📁 Project Structure

```
backend/
├── config/          # Django settings, root URL conf, ASGI/WSGI
├── users/           # Custom user model, registration, profile
├── products/        # Products, categories, EAV attributes/values
├── orders/          # Addresses, orders, order items
├── carts/           # Shopping cart and cart items
├── payments/        # Stripe integration, transactions, stock reservations
└── reviews/         # Product reviews with moderation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- A [Stripe](https://stripe.com) account (for payment features)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/h-taimoury/Django_E_Commerce.git
cd Django_E_Commerce/backend

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your values (see Environment Variables section below)

# 5. Run database migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DEBUG=True
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYMENT_SUCCESS_URL=http://localhost:3000/payment/success
```

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/users/register/` | Register a new user |
| `POST` | `/api/users/login/` | Login and receive JWT tokens |
| `GET/PATCH` | `/api/users/me/` | View or update current user profile |

### Products
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/products/` | List all active products |
| `GET` | `/api/products/{id}/` | Product detail with specifications |
| `GET` | `/api/categories/` | List all categories |
| `GET` | `/api/attributes/` | List all product attributes |

### Cart
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/cart/` | View current cart |
| `POST` | `/api/cart/items/` | Add item to cart |
| `PATCH/DELETE` | `/api/cart/items/{id}/` | Update or remove cart item |
| `POST` | `/api/cart/clear/` | Clear the cart |

### Orders
| Method | Endpoint | Description |
|---|---|---|
| `GET/POST` | `/api/orders/` | List orders or create a new draft order |
| `GET` | `/api/orders/{id}/` | Order detail |
| `GET/POST` | `/api/addresses/` | List or create shipping addresses |

### Payments
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/payments/create-session/` | Create a Stripe Checkout session |
| `POST` | `/api/payments/webhook/` | Stripe webhook handler |

### API Documentation
| Endpoint | Description |
|---|---|
| `/api/schema/swagger-ui/` | Interactive Swagger UI |
| `/api/schema/` | Raw OpenAPI schema (JSON/YAML) |

---

## 🔄 Order & Payment Flow

```
1. User adds items to Cart
2. POST /api/orders/         → Creates a draft Order
3. POST /api/payments/create-session/
        → Reserves stock (decrements quantity_available)
        → Creates a Stripe Checkout Session
        → Order moves to pending_payment
4. User completes payment on Stripe-hosted page
5. Stripe sends checkout.session.completed webhook
        → Stock consumed (decrements quantity_on_hand)
        → Order moves to paid
6. If session expires → stock released, Order moves to expired
```

---

## 🧪 Running Tests

```bash
python manage.py test
```

Tests are organized per app and cover authentication, product CRUD, order isolation, and permission boundaries.

---

## 🔐 Permissions

| Role | Capabilities |
|---|---|
| **Anonymous** | Browse products, categories, attributes |
| **Authenticated User** | Manage own cart, orders, addresses, and reviews |
| **Admin (is_staff)** | Full CRUD on products, attributes, options; view all transactions; approve reviews |


