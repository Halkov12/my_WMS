# Warehouse Management System (WMS)

Modern warehouse management system built with Django using Bootstrap 5 and interactive components.

## 🚀 Features

### 📦 Product Management
- Create and edit products
- Product categorization
- Product photo upload
- Barcodes and unique identifiers
- Product search and filtering

### 🔄 Warehouse Operations
- **Product Receipt** - receiving products to warehouse
- **Product Issue** - issuing products from warehouse
- **Product Write-off** - writing off damaged or lost products
- Detailed logging of all operations
- Change history with user tracking

### 📊 Reports & Analytics
- Product reports with PDF/Excel export
- Operation reports with period filtering
- Change logs for audit
- Interactive dashboard charts
- Category statistics

### 🛠️ Tools (Managers Only)
- **Import/Export** - bulk product upload from CSV/Excel
- **Backup** - data backup and restore
- **Barcode Generator** - Code 128 barcode creation
- **Full Backup** - complete system data backup

### 👥 Role System
- **Manager** - full access to all functions
- **Seller** - issue and write-off operations
- **Worker** - product and operation viewing

### 📱 Responsive Design
- Bootstrap 5 for modern interface
- Mobile navigation
- Dark/light theme
- Interactive components

## 🛠️ Technologies

- **Backend**: Django 4.2+
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite/PostgreSQL
- **Money**: django-money
- **Barcodes**: python-barcode
- **Export**: openpyxl, pandas
- **Reports**: reportlab

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- pip

## 🚀 Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd my_WMS
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

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

### 7. Run Server
```bash
python manage.py runserver
```

System will be available at: http://127.0.0.1:8000/

## ⚙️ Configuration

### Environment Variables
Create `.env` file in project root:

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

## 📖 Usage

### Getting Started
1. **Login** - use email and password
2. **Create Products** - go to "Receipt" → "Create New Product"
3. **Perform Operations** - use appropriate sections for receipt/issue/write-off
4. **View Reports** - available in "Reports" section

### User Roles

#### Manager
- Full access to all functions
- Product and operation management
- Access to tools (import/export, backup)
- Report generation

#### Seller
- Product viewing
- Product issue
- Product write-off
- Access to barcode generator

#### Worker
- Product viewing
- Operation viewing
- Access to barcode generator

### Product Import
1. Prepare CSV or Excel file with columns:
   - `name` - product name (required)
   - `quantity` - quantity (required)
   - `purchase_price` - purchase price (required)
   - `sale_price` - sale price (required)
   - `barcode` - barcode (optional)
   - `category` - category (optional)
   - `unit` - unit of measurement (optional)
   - `description` - description (optional)

2. Go to "Tools" → "Import Products"
3. Upload file and preview
4. Confirm import

### Backup
- **Product Backup** - product data only
- **Full Backup** - complete system data
- Files saved in JSON format
- Automatic naming with date and time

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

## 📁 Project Structure

```
my_WMS/
├── src/                    # Main Django code
│   ├── accounts/          # User management
│   ├── api/              # API endpoints
│   ├── common/           # Shared models and utilities
│   ├── config/           # Django settings
│   ├── templates/        # HTML templates
│   └── wms/             # Main WMS logic
├── docs/                 # Documentation
├── nginx/               # Nginx configuration
├── commands/            # Run scripts
├── requirements.txt     # Python dependencies
├── docker-compose.yml   # Docker Compose
└── README.md           # This file
```

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

## 📚 Documentation

Detailed documentation available in the system:
- Go to "Tools" → "Help"
- Or open http://127.0.0.1:8000/help/

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is distributed under the MIT License. See `LICENSE` file for details.

## 📞 Support

If you have questions or issues:
- Create an Issue in the repository
- Check the documentation in the system
- Review FAQ in the help section

## 🔄 Updates

To update the system:
```bash
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```

---

**Warehouse Management System** - modern warehouse management solution 🚀