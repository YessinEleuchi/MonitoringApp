# 🚀 System Monitoring Application

A robust and scalable system monitoring application built with FastAPI, designed to track and analyze application performance metrics in real-time.

## ✨ Features

- 📊 Real-time application monitoring
- 🔄 Endpoint health checks
- 📈 Performance metrics tracking
- ⚡ FastAPI-powered REST API
- 🔐 User authentication and authorization
- 📱 Responsive dashboard
- 🔔 Alert system for threshold violations

## 🛠️ Tech Stack

- **Backend Framework:** FastAPI
- **Database:** MySQL
- **ORM:** SQLAlchemy
- **Task Scheduler:** APScheduler
- **HTTP Client:** HTTPX
- **Data Validation:** Pydantic

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL Server
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YessineELEUCHI/system-monitoring-app.git
cd system-monitoring-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python create_db.py
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## 📁 Project Structure

```
MonitoringApp/
├── app/
│   ├── core/           # Core functionality
│   ├── models/         # Database models
│   ├── routers/        # API endpoints
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   └── main.py         # Application entry point
├── venv/               # Virtual environment
├── requirements.txt    # Project dependencies
└── create_db.py        # Database initialization
```

## 🔧 Configuration

The application uses environment variables for configuration. Create a `.env` file in the root directory with the following variables:

```env
DATABASE_URL=mysql://user:password@localhost:3306/monitoring_db
SECRET_KEY=your-secret-key
```

## 📝 API Documentation

Once the application is running, you can access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Yessine ELEUCHI**
- GitHub: [@YessineELEUCHI](https://github.com/YessinEleuchi)

## 🙏 Acknowledgments

- FastAPI documentation
- SQLAlchemy documentation
- All contributors and supporters of the project
