# 🏠 Flask Property Listing & Management System

A **Real Estate Property Listing Web Application** built using **Flask** and **SQLite**.
This application supports **Owners** and **Buyers** with role-based access and complete property management features.

---

## 🎯 Project Goal

Learn and practice:

* Flask fundamentals
* Authentication & session handling
* Role-based access control
* File uploads
* Raw SQL queries with SQLite
* Clean and structured Flask project architecture

---

## ✨ Features

### 🔐 Authentication

* User Registration (**Owner / Buyer**)
* Login & Logout
* Forgot Password (**OTP-based**)
* Change Password
* Flash messages for user feedback

---

### 🏘️ Owner Features

* Owner Dashboard
* Add Property (**with image upload**)
* Edit Property
* Delete Property
* View **My Properties**

**Property Fields:**

* Title
* Property Type (Apartment / House)
* Deal Type (Sale / Rent)
* Price
* Contact Number
* State, City, Area
* Status

---

### 🛒 Buyer Features

* Buyer Dashboard
* View all available properties
* Filter properties by:

  * State
  * City
  * Deal Type (Sale / Rent)
  * Maximum Price
* View detailed property page
* **Buy / Rent** button based on deal type

---

### 🖼️ Image Upload

* Property images stored in:

```text
static/uploads/
```

* Images rendered dynamically in property cards

---

## 🧱 Project Structure

```text
PRACTICE_/
│
├── static/
│   └── uploads/
│
├── templates/
│   ├── add_property.html
│   ├── buyer_dashboard.html
│   ├── buyer_properties.html
│   ├── changepassword.html
│   ├── edit_property.html
│   ├── forgotpassword.html
│   ├── home.html
│   ├── login.html
│   ├── main.html
│   ├── my_properties.html
│   ├── otppage.html
│   ├── owner_dashboard.html
│   ├── property_details.html
│   ├── register.html
│   ├── success.html
│   └── view_properties.html
│
├── venv/                # Virtual environment (ignored in Git)
├── .env                 # Environment variables (ignored in Git)
├── app.py               # Main Flask application
├── users.db             # SQLite database
├── requirements.txt
└── README.md
```

---

## 🛠️ Tech Stack

| Layer          | Technology           |
| -------------- | -------------------- |
| Backend        | Flask                |
| Database       | SQLite               |
| Templates      | Jinja2               |
| Frontend       | HTML, CSS            |
| Authentication | Flask Sessions       |
| File Upload    | Werkzeug             |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### 2️⃣ Create & Activate Virtual Environment

**Windows**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables (`.env`)

Create a `.env` file in the project root:

```env
MAIL_ID=vasudevgo.tagline@gmail.com
MAIL_PASSWORD=your_email_app_password
```

⚠️ Do not commit .env to Git it contains senitive information.

---

## 🗄️ Database Usage (SQLite)

### ✅ Shared Database Login (Learning Purpose)

* This project uses **SQLite (`users.db`)**
* The database file is **included in the repository**


---

## ▶️ Running the Application

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000
```

---

## 🔑 User Roles

### 👤 Owner

* Add, edit, and delete properties
* View own listed properties

### 🧑 Buyer

* Browse all available properties
* Filter and view property details
* Buy or rent based on deal type

---

## ❗ Error Handling

* Duplicate username detection
* Invalid login credentials
* Unauthorized access prevention
* Missing form fields
* Cache prevention using response headers

---

## 🔒 Security Notes

* Session-based authentication
* Cache disabled for logout protection
* `.env` ignored by Git
* Raw SQL used intentionally for learning

---

## 📌 Future Enhancements

* Password hashing
* Email-based password reset
* Admin dashboard
* Pagination
* Property approval system
* SQLAlchemy migration
* Deployment (Render / Railway / AWS)

---

## 👨‍💻 Author

Vasudev Gol Github => https://github.com/vasudevgotagline-star

⭐ *If this project helped you, consider giving it a star on GitHub!*

