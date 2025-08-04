# Jira Ticket Supporter

A modern, production-ready chat interface to interact with Jira via an AI agent, featuring a custom AI agent tool to automatically triage newly created Jira tickets.

## 🚀 Overview

This project provides a sophisticated AI-powered Jira assistant that enables natural language interaction with Jira through a beautiful web interface. Built with modern best practices, comprehensive error handling, and production-ready architecture.

### Key Features

- **🤖 AI-Powered Jira Integration**: Natural language interaction with Jira
- **🔗 Automatic Ticket Triage**: AI agent automatically links related issues and generates user stories
- **📊 Real-time Health Monitoring**: Comprehensive system health checks and monitoring
- **🛡️ Production-Ready Security**: Environment-based configuration and security headers
- **📱 Responsive Design**: Mobile-first approach with modern UI/UX
- **🔧 Comprehensive Logging**: Structured logging throughout the application
- **⚡ High Performance**: Optimized database queries and API calls

## 🏗️ Architecture

The project follows a modern microservices architecture with clear separation of concerns:

### Backend (Django)
- **RESTful API**: Django REST Framework with comprehensive endpoints
- **Database**: PostgreSQL with pgvector for vector operations
- **AI Integration**: LangChain agents with CO-STAR prompting
- **Security**: Environment-based configuration and proper authentication
- **Monitoring**: Health checks, logging, and error tracking

### Frontend (Mesop)
- **Modern UI**: Google Mesop framework for rapid AI app development
- **Reactive State**: Real-time state management and updates
- **Error Handling**: Graceful error recovery and user feedback
- **Responsive Design**: Mobile-first approach with adaptive layouts

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.8+**: Modern Python with type hints and comprehensive documentation
- **Django 5.1+**: High-level web framework with REST API
- **PostgreSQL**: Robust database with pgvector extension
- **Google Mesop**: Modern Python web framework for AI applications
- **LangChain**: AI agent framework with advanced prompting strategies

### AI & ML
- **OpenAI GPT**: Large language model for natural language processing
- **CO-STAR Prompting**: Structured prompt engineering framework
- **Chain-of-Thought (CoT)**: Advanced reasoning capabilities
- **Few-Shot Learning**: Example-based learning for better responses

### DevOps & Monitoring
- **Docker**: Containerized deployment with docker-compose
- **Health Checks**: Comprehensive system monitoring
- **Structured Logging**: Detailed logging for debugging and monitoring
- **Error Tracking**: Graceful error handling and recovery

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- OpenAI API Key
- Jira API Token
- Jira Username
- Jira Instance URL

### 1. Configuration
Update the configuration file with your credentials:

```bash
# config/config.ini
[DEV]
JIRA_API_TOKEN=your-jira-api-token
JIRA_USERNAME=your-jira-username
JIRA_INSTANCE_URL=https://your-instance.atlassian.net
OPENAI_API_KEY=your-openai-api-key
PROJECT_KEY=your-project-key
ENVIRONMENT=development
SECRET_KEY=your-secret-key
```

### 2. Run the Application
```bash
# Start all services
docker compose up --build

# Access the application
# Frontend: http://localhost:8080/
# Backend API: http://localhost:8000/
# Health Check: http://localhost:8080/health
```

### 3. Test the Configuration
```bash
# Test Jira configuration
docker exec django python manage.py test_jira_config --verbose

# Check API health
curl http://localhost:8000/api/health-check/
```

## 📊 Features

### AI Agent Capabilities
- **Natural Language Processing**: Understand and process natural language requests
- **Jira Integration**: Create, update, and query Jira tickets
- **Automatic Triage**: Link related tickets and generate metadata
- **User Story Generation**: Create user stories and acceptance criteria
- **Priority Assessment**: Automatically assess ticket priorities

### User Interface
- **Chat-like Interface**: Natural conversation with the AI agent
- **Example Prompts**: Pre-built examples for common tasks
- **Real-time Feedback**: Live updates and progress indicators
- **Error Recovery**: Graceful error handling and user guidance
- **Mobile Responsive**: Works seamlessly on all devices

### System Monitoring
- **Health Checks**: Comprehensive system health monitoring
- **Performance Metrics**: Request/response timing and logging
- **Error Tracking**: Detailed error logging and recovery
- **Configuration Validation**: Environment variable validation

## 🔧 API Endpoints

### Core Endpoints
```bash
# Health Check
GET /api/health-check/

# Jira Agent
POST /api/jira-agent/
{
    "request": "Create a new task with description 'Bug fix'"
}

# Records (Paginated)
GET /api/records/?page=1&page_size=20

# Record Details
GET /api/records/1/
```

### Health Monitoring
```bash
# System Health
GET /health

# API Health
GET /api/health-check/

# Configuration Status
GET /health (includes config validation)
```

## 🛡️ Security Features

### Production Security
- **Environment-based Configuration**: No hardcoded secrets
- **Security Headers**: HSTS, XSS protection, content type sniffing
- **Input Validation**: Comprehensive request validation
- **Error Handling**: No sensitive data exposure in errors

### Authentication & Authorization
- **Jira API Authentication**: Secure API token management
- **Request Validation**: Input sanitization and validation
- **Rate Limiting**: Configurable request limits
- **Timeout Management**: Proper request timeouts

## 📈 Performance Optimizations

### Database Performance
- **Indexing**: Optimized database indexes for common queries
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized database queries
- **Pagination**: Efficient handling of large datasets

### API Performance
- **Caching**: Response caching for improved performance
- **Concurrent Processing**: Thread pool for ticket linking
- **Retry Logic**: Exponential backoff for failed requests
- **Timeout Management**: Configurable request timeouts

## 🔍 Monitoring & Logging

### Health Monitoring
- **System Health**: Real-time system status monitoring
- **API Health**: Django API connectivity checks
- **Database Health**: Database connection monitoring
- **Agent Health**: AI agent availability checks

### Logging
- **Structured Logging**: Comprehensive logging throughout
- **Error Tracking**: Detailed error logging and context
- **Performance Monitoring**: Request/response timing
- **Audit Trail**: Complete request/response logging

## 🧪 Testing

### Configuration Testing
```bash
# Test Jira configuration
python manage.py test_jira_config --verbose

# Test API connectivity
curl http://localhost:8000/api/health-check/
```

### Health Checks
- **Configuration Validation**: Environment variable checks
- **API Connectivity**: Django API health checks
- **Database Connectivity**: Database connection tests
- **Agent Availability**: AI agent status checks

## 🚀 Deployment

### Docker Deployment
```bash
# Production deployment
docker compose -f docker-compose.yml up -d

# Development deployment
docker compose up --build
```

### Environment Configuration
```bash
# Production environment
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key

# Development environment
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-development-secret-key
```

## 📚 Documentation

### API Documentation
- **Health Check**: `/api/health-check/`
- **Jira Agent**: `/api/jira-agent/`
- **Records**: `/api/records/`
- **Record Details**: `/api/records/{id}/`

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Follow the coding standards (type hints, docstrings, error handling)
4. Add comprehensive tests
5. Submit a pull request

### Code Standards
- **Type Hints**: All functions must have type annotations
- **Docstrings**: Comprehensive documentation following PEP 257
- **Error Handling**: Proper exception handling and logging
- **Testing**: Unit tests for all new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Mesop**: Modern Python web framework for AI applications
- **LangChain**: AI agent framework and tools
- **Django**: High-level Python web framework
- **OpenAI**: Large language model capabilities
- **Atlassian**: Jira API and integration

## 🔗 References

- [Google Mesop Documentation](https://google.github.io/mesop/)
- [LangChain Documentation](https://python.langchain.com/)
- [Django Documentation](https://docs.djangoproject.com/)
- [Jira REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

