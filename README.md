# Warehouse Management System (WMS)

A modern warehouse management system built with Django, Bootstrap 5, and interactive components.

---

## 🚀 Features

### 📦 Product Management
- Create, edit, and categorize products
- Product photo upload
- Barcodes and unique identifiers
- Product search and filtering

### 🔄 Warehouse Operations
- **Product Receipt**: Add products to warehouse stock
- **Product Issue**: Remove products from warehouse stock
- **Product Write-off**: Write off damaged or lost products
- Detailed logging of all operations
- Change history with user tracking

### 📊 Reports & Analytics
- Product reports with PDF/Excel export
- Operation reports with period filtering
- Change logs for audit
- Interactive dashboard charts
- Category statistics

### 🛠️ Tools (Managers Only)
- **Import/Export**: Bulk product upload from CSV/Excel
- **Backup**: Data backup and restore (products or full system)
- **Barcode Generator**: Create Code 128 barcodes
- **Inventory Creation**: Start a new inventory check
- **Send Email**: Notify managers or staff
- **User Management**: Add, edit, or remove users

### 👥 Role System
- **Manager**: Full access to all functions
- **Seller**: Issue and write-off operations
- **Worker**: View products and operations

### 📱 Responsive Design
- Bootstrap 5 for a modern interface
- Mobile navigation
- Dark/light theme
- Interactive components

---

## 🛠️ Technologies

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite or PostgreSQL
- **Money**: django-money
- **Barcodes**: python-barcode
- **Export**: openpyxl, pandas
- **Reports**: reportlab

---

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- pip

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Halkov12/my_WMS.git
cd my_WMS
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Database Setup
```bash
cd src
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run the Server
```bash
python manage.py runserver
```

The system will be available at: http://127.0.0.1:8000/

---

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Database Configuration
To use PostgreSQL, modify settings in `src/config/settings/base.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'wms_db',
        'USER': 'wms_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📖 Usage

### Getting Started
1. **Login** with your email and password
2. **Create Products** via "Receipt" → "Create New Product"
3. **Perform Operations**: Use the appropriate section for receipt, issue, or write-off
4. **View Reports** in the "Reports" section

### User Roles

#### Manager
- Full access to all features
- Product and operation management
- Access to all tools (import/export, backup, inventory, email, user management)
- Report generation

#### Seller
- View products
- Issue and write-off products
- Access barcode generator

#### Worker
- View products and operations
- Access barcode generator

### Product Import
1. Prepare a CSV or Excel file with columns:
   - `name` (required)
   - `quantity` (required)
   - `purchase_price` (required)
   - `sale_price` (required)
   - `barcode` (optional)
   - `category` (optional)
   - `unit` (optional)
   - `description` (optional)
2. Go to "Tools" → "Import Products"
3. Upload and preview the file
4. Confirm import

### Backup
- **Product Backup**: Only product data
- **Full Backup**: Complete system data
- Files are saved in JSON format with automatic naming (date/time)

### Inventory Creation
- Go to "Tools" → "Create Inventory"
- Fill in the required information and confirm to start a new inventory check

---

## 🐳 Docker

### Run with Docker Compose
```bash
docker-compose up -d
```

### Build Docker Image
```bash
docker build -t wms .
docker run -p 8000:8000 wms
```

---

## 📁 Project Structure

```
my_WMS/
├── src/                    # Main Django code
│   ├── accounts/           # User management
│   ├── api/                # API endpoints
│   ├── common/             # Shared models and utilities
│   ├── config/             # Django settings
│   ├── templates/          # HTML templates
│   └── wms/                # Main WMS logic
├── docs/                   # Documentation
├── nginx/                  # Nginx configuration
├── commands/               # Run scripts
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker Compose
└── README.md               # This file
```

---

## 🔧 Development

### Run Tests
```bash
python manage.py test
```

### Create Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Create Fixtures
```bash
python manage.py dumpdata > fixtures/initial_data.json
```

---

## 📚 Documentation

- In-app: Go to "Tools" → "Help"
- Or open http://127.0.0.1:8000/help/

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See the `LICENSE` file for details.

---

## 📞 Support

- Create an Issue in the repository
- Check the in-app documentation
- Review the FAQ in the help section

---

## 🔄 Updates

To update the system:
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

---

**Warehouse Management System** – a modern solution for efficient warehouse operations 🚀