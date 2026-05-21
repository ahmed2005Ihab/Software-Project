# 🏠 HomeCraft - Furniture E-Commerce Website

<div align="center">

![Flask](https://img.shields.io/badge/Flask-3.0.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**A complete online furniture store built with Python and Flask**

*Perfect for learning web development and software design patterns!*

[Quick Start](#-quick-start-3-steps) • [Features](#-what-can-it-do) • [How It Works](#-how-it-works) • [Learning Resources](#-what-youll-learn)

</div>

---

## 📖 What is HomeCraft?

HomeCraft is a **fully functional online furniture store** - think of it like a mini Amazon, but just for furniture! 

This project was built to demonstrate **professional software development practices** in a real-world application. It's perfect for:
- 🎓 **Students** learning web development
- 💼 **Developers** wanting to see clean code architecture
- 🚀 **Anyone** building their first e-commerce site

### What Makes It Special?

✅ **Complete Features** - Not just a demo! It has everything a real store needs  
✅ **Clean Code** - Organized using professional design patterns  
✅ **Well Tested** - Includes automated tests to ensure everything works  
✅ **Easy to Run** - Works on Windows, Mac, and Linux  
✅ **Beginner Friendly** - Clear code structure and documentation  

---

## 🎯 What Can It Do?

### For Shoppers 🛍️

| Feature | What It Does |
|---------|--------------|
| 👤 **Create Account** | Sign up with email and password |
| 🔐 **Login/Logout** | Secure access to your account |
| 🪑 **Browse Products** | See all furniture items with pictures and prices |
| 🏷️ **Filter by Category** | Find Sofas, Tables, Beds, Storage, or Lighting |
| 🛒 **Shopping Cart** | Add items, change quantities, see total price |
| ❤️ **Wishlist** | Save favorite items for later |
| 📦 **Place Orders** | Buy items and see order history |
| ⭐ **Write Reviews** | Rate products and share your thoughts |
| 💬 **Send Feedback** | Contact the store with suggestions |

### For Store Owners 👨‍💼

| Feature | What It Does |
|---------|--------------|
| 📊 **Dashboard** | See overview of your store |
| ➕ **Add Products** | Create new furniture listings |
| ✏️ **Edit Products** | Update prices, descriptions, and images |
| 🗑️ **Delete Products** | Remove items from the store |
| 📋 **Manage Orders** | View all customer orders |
| 👥 **Manage Users** | See registered customers |
| 📦 **Track Inventory** | Monitor stock levels |

---

## 🚀 Quick Start (3 Steps!)

### What You Need First

Before starting, make sure you have:
- **Python 3.8 or newer** ([Download here](https://www.python.org/downloads/))
- **A code editor** (like VS Code, PyCharm, or even Notepad++)
- **Basic command line knowledge** (don't worry, we'll guide you!)

### Step 1: Get the Code

Open your terminal/command prompt and type:

```bash
# Download the project
git clone https://github.com/ahmed2005Ihab/Software-Project.git

# Go into the project folder
cd Software-Project
```

> 💡 **Don't have Git?** You can also download the ZIP file from GitHub and extract it!

### Step 2: Set Up Python Environment

```bash
# Create a virtual environment (keeps this project's files separate)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

> 💡 **What's a virtual environment?** Think of it as a separate workspace for this project, so it doesn't mess with other Python projects on your computer!

### Step 3: Run the Website!

```bash
python main.py
```

That's it! 🎉 Now open your web browser and go to:
```
http://localhost:5000
```

### 🔑 First Login

The app creates a default admin account for you:
- **Email:** `admin@homecraft.com`
- **Password:** `admin123`

> ⚠️ **Important:** Change this password after logging in!

---

## 📁 Understanding the Project Structure

Here's what each folder does (simplified!):

```
Software-Project/
│
├── 📂 controllers/          # Handles what happens when you click buttons
│   ├── auth.py             # Login, register, logout
│   ├── products.py         # Showing products
│   ├── cart.py             # Shopping cart actions
│   ├── admin.py            # Admin dashboard
│   └── ...
│
├── 📂 models/               # Defines what data looks like
│   ├── user.py             # User information (name, email, password)
│   ├── product.py          # Product details (name, price, image)
│   ├── cart.py             # Shopping cart items
│   ├── order.py            # Customer orders
│   └── ...
│
├── 📂 repositories/         # Talks to the database
│   ├── user_repository.py  # Save/get user data
│   ├── product_repository.py  # Save/get product data
│   └── ...
│
├── 📂 Templates/            # HTML files (what you see in browser)
│   ├── index.html          # Homepage
│   ├── login.html          # Login page
│   ├── products.html       # Product listing
│   └── ...
│
├── 📂 static/               # Images, CSS, JavaScript
│   ├── css/                # Styling
│                  
│   └── images/             # Pictures
│
├── 📂 tests/                # Automated tests
│
├── 📄 app.py               # Sets up the Flask application
├── 📄 main.py              # Starts the website (run this!)
├── 📄 requirements.txt     # List of required packages
└── 📄 README.md            # This file!
```

---

## 🎓 What You'll Learn

This project is a great learning resource! Here's what it demonstrates:

### 1. **Web Development Basics**
- How to build a website with Python and Flask
- Creating web pages with HTML templates
- Handling user input from forms
- Managing user sessions (login/logout)

### 2. **Database Management**
- Storing data in a database (SQLite)
- Creating relationships between data (users have orders, products have reviews)
- Saving, updating, and deleting information

### 3. **Professional Code Organization**
- **MVC Pattern** - Separating code into Models (data), Views (HTML), and Controllers (logic)
- **Repository Pattern** - Keeping database code separate from business logic
- **Factory Pattern** - Creating objects in a smart, organized way
- **Singleton Pattern** - Ensuring only one database connection exists

### 4. **Security Best Practices**
- Password hashing (never storing passwords in plain text!)
- User authentication (checking who you are)
- Protected routes (some pages only for logged-in users)

### 5. **Testing**
- Writing automated tests to check if code works
- Testing different parts of the application
- Ensuring changes don't break existing features

---

## 🔌 Main Website Pages

Here are the main pages you can visit:

### Anyone Can Access:
- `http://localhost:5000/` - Homepage
- `http://localhost:5000/products` - Browse all products
- `http://localhost:5000/auth/login` - Login page
- `http://localhost:5000/auth/register` - Create account
- `http://localhost:5000/feedback` - Send feedback

### After Logging In:
- `http://localhost:5000/cart` - Your shopping cart
- `http://localhost:5000/profile` - Your profile
- `http://localhost:5000/orders` - Your order history
- `http://localhost:5000/wishlist` - Your saved items

### Admin Only:
- `http://localhost:5000/admin/dashboard` - Admin control panel
- `http://localhost:5000/admin/products` - Manage products
- `http://localhost:5000/admin/orders` - View all orders
- `http://localhost:5000/admin/users` - Manage users

---

## 🧪 Testing the Code

Want to make sure everything works? Run the tests!

```bash
# Run all tests
pytest

# Run tests with more details
pytest -v

# See which parts of code are tested
pytest --cov
```

**What gets tested:**
- ✅ User registration and login
- ✅ Adding products to cart
- ✅ Creating orders
- ✅ Admin functions
- ✅ Database operations
- ✅ Error handling

---

## 🐳 Running with Docker (Alternative Method)

Docker lets you run the app without installing Python or packages manually!

### What is Docker?
Think of Docker as a "ready-to-go box" that has everything the app needs already inside it.

### Using Docker:

```bash
# Start the application (downloads and sets up everything automatically!)
docker-compose up

# Stop the application
docker-compose down
```

Then visit `http://localhost:5000` in your browser!

> 💡 **Need Docker?** Download it from [docker.com](https://www.docker.com/get-started)

---

## 🛠️ Built With

| Technology | What It Does | Why We Use It |
|------------|--------------|---------------|
| **Python** | Programming language | Easy to learn, powerful for web apps |
| **Flask** | Web framework | Makes building websites simple |
| **SQLAlchemy** | Database tool | Lets us work with databases using Python |
| **SQLite** | Database | Stores all data (users, products, orders) |
| **Flask-Login** | Authentication | Handles user login/logout |
| **Werkzeug** | Security | Keeps passwords safe |
| **Pytest** | Testing | Checks if code works correctly |
| **HTML/CSS/JS** | Frontend | What you see in the browser |

---

## 💡 Common Questions

### How do I add my own products?

1. Run the app and login as admin
2. Go to `http://localhost:5000/admin/products`
3. Click "Add New Product"
4. Fill in the details and submit!

### Where is the database stored?

In the `instance/` folder as `homecraft.db`. It's created automatically when you first run the app.

### Can I change the design?

Yes! Edit the files in:
- `Templates/` for HTML structure
- `static/css/` for styling
- `static/js/` for interactive features

### How do I reset everything?

Delete the `instance/homecraft.db` file and run `python main.py` again. This creates a fresh database!

### I got an error, what do I do?

1. Make sure you activated the virtual environment
2. Check that all packages are installed: `pip install -r requirements.txt`
3. Make sure port 5000 isn't being used by another program
4. Check the error message - it usually tells you what's wrong!

---

## 🎨 How It Works (Simple Explanation)

Let's say a customer wants to buy a sofa:

```
1. Customer clicks "Add to Cart" on a sofa
   ↓
2. Browser sends request to controllers/cart.py
   ↓
3. Controller asks repositories/cart_repository.py to save the item
   ↓
4. Repository saves it in the database (instance/homecraft.db)
   ↓
5. Controller sends back a success message
   ↓
6. Browser shows "Item added to cart!"
```

This separation makes the code:
- ✅ **Easier to understand** - Each file has one job
- ✅ **Easier to test** - Test each part separately
- ✅ **Easier to change** - Change database without touching controllers
- ✅ **More professional** - Industry-standard organization

---

## 🚀 Next Steps

Want to improve this project? Here are some ideas:

### Beginner Level:
- [ ] Change the colors and styling
- [ ] Add more product categories
- [ ] Customize the homepage
- [ ] Add more product images

### Intermediate Level:
- [ ] Add a search feature
- [ ] Implement product filtering by price
- [ ] Add email notifications for orders
- [ ] Create a "Featured Products" section

### Advanced Level:
- [ ] Add payment integration (Stripe, PayPal)
- [ ] Implement product recommendations
- [ ] Add real-time chat support
- [ ] Create a mobile app version
- [ ] Switch to PostgreSQL for production
- [ ] Deploy to a cloud platform (Heroku, AWS)

---

## 📚 Learning Resources

Want to learn more? Check out:

- **Flask Documentation:** [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- **Python Tutorial:** [python.org/about/gettingstarted](https://www.python.org/about/gettingstarted/)
- **SQLAlchemy Docs:** [docs.sqlalchemy.org](https://docs.sqlalchemy.org/)
- **Web Development:** [MDN Web Docs](https://developer.mozilla.org/)

---

## 🤝 Contributing

This is a learning project, so contributions are welcome! Whether you:
- 🐛 Found a bug
- 💡 Have an idea for improvement
- 📝 Want to improve documentation
- ✨ Want to add a feature

Feel free to open an issue or submit a pull request!

---

## ⚠️ Important Notes

### For Learning:
- ✅ Great for learning web development
- ✅ Perfect for school projects
- ✅ Good portfolio piece

### For Production:
If you want to use this for a real business, you should:
- 🔒 Change the secret key in `app.py`
- 🔒 Use a stronger database (PostgreSQL/MySQL)
- 🔒 Add HTTPS/SSL certificates
- 🔒 Implement proper payment processing
- 🔒 Add email verification
- 🔒 Set up proper hosting

---

## 🎓 About This Project

This project was created as part of a **Software Engineering course** to demonstrate:
- Professional code organization
- Design pattern implementation
- Full-stack web development
- Test-driven development
- Clean architecture principles

It's meant to be a **learning resource** that shows how to build a real-world application the right way!

---

## 👨‍💻 Authors

**Ahmed Ihab** - [GitHub Profile](https://github.com/ahmed2005Ihab)
**Ahmed Assem** - [GitHub Profile](https://github.com/AhmedTolba98341)
**Jasmin Nasser** - [GitHub Profile](https://github.com/jasmin-nasser)
**Bassant Mohamed** - [GitHub Profile](https://github.com/Bassant-27)

---

## 📄 License

This project is open source and available for educational purposes. Feel free to use it to learn, teach, or build upon!

---

<div align="center">

### 🌟 Found this helpful? Give it a star!

**Happy Coding! 🚀**

*Made with ❤️ and Python*

---

**Questions?** Open an issue on GitHub!  
**Want to learn more?** Check out the code and comments!

</div>
