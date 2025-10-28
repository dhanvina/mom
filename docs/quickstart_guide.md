# MOM Quickstart Guide

Welcome to MOM (Modular Object Management)! This guide will help new contributors get up and running quickly with local development, testing, and usage.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Installation](#local-installation)
- [Testing](#testing)
- [Usage](#usage)
  - [CLI Interface](#cli-interface)
  - [Streamlit UI](#streamlit-ui)
- [Development Workflow](#development-workflow)
  - [Pre-commit Hooks](#pre-commit-hooks)
  - [CI Checks](#ci-checks)
- [Sample Configuration](#sample-configuration)
- [System Flow Diagram](#system-flow-diagram)
- [Next Steps](#next-steps)

## Prerequisites

- Python 3.8 or higher
- Git
- pip or conda
- Virtual environment tool (recommended)

## Local Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/dhanvina/mom.git
cd mom
```

### Step 2: Create and Activate Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n mom python=3.8
conda activate mom
```

### Step 3: Install Dependencies

```bash
# Install main dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Step 4: Environment Setup

```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Edit configuration as needed
vim config/config.yaml  # or your preferred editor
```

## Testing

### Step 1: Run Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mom --cov-report=html

# Run specific test file
pytest tests/test_core.py
```

### Step 2: Run Integration Tests

```bash
# Run integration tests
pytest tests/integration/

# Run with verbose output
pytest -v tests/integration/
```

### Step 3: Verify Installation

```bash
# Test CLI
mom --version
mom --help

# Test basic functionality
mom status
```

## Usage

### CLI Interface

The MOM CLI provides powerful command-line tools for object management:

#### Basic Commands

```bash
# Initialize a new MOM workspace
mom init

# Check system status
mom status

# List available objects
mom list

# Create a new object
mom create --type module --name my_module

# Update an existing object
mom update --id 12345 --field name --value "New Name"

# Delete an object
mom delete --id 12345

# Search objects
mom search --query "keyword"

# Export configuration
mom export --format yaml --output config.yaml
```

#### Advanced Commands

```bash
# Batch operations
mom batch --file operations.json

# Sync with remote
mom sync --remote production

# Generate reports
mom report --type summary --format html

# Backup data
mom backup --destination ./backups/
```

### Streamlit UI

For a user-friendly web interface, use the Streamlit application:

#### Step 1: Start the Streamlit Server

```bash
# Start with default config
streamlit run app/streamlit_app.py

# Start with custom config
streamlit run app/streamlit_app.py -- --config config/custom.yaml

# Start on custom port
streamlit run app/streamlit_app.py --server.port 8502
```

#### Step 2: Access the Web Interface

1. Open your browser to `http://localhost:8501`
2. Navigate through the sidebar menu:
   - **Dashboard**: Overview of system status
   - **Object Manager**: Create, read, update, delete objects
   - **Search**: Advanced search functionality
   - **Configuration**: System settings
   - **Reports**: Generate and view reports
   - **Help**: Documentation and tutorials

#### Key Features

- **Interactive Object Creation**: Form-based object creation with validation
- **Real-time Search**: Dynamic filtering and search with live results
- **Visual Reports**: Charts and graphs for data visualization
- **Bulk Operations**: Upload CSV files for batch processing
- **Export Functionality**: Download data in various formats (CSV, JSON, YAML)

## Development Workflow

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install hooks (run once after cloning)
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

**Enabled Hooks:**
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning
- **pytest**: Run tests

### CI Checks

Continuous Integration runs automatically on pull requests:

**GitHub Actions Workflows:**
- **Test Suite**: Runs on Python 3.8, 3.9, 3.10, 3.11
- **Code Quality**: Linting, formatting, type checking
- **Security Scan**: Dependency vulnerability checking
- **Documentation**: Build and deploy docs
- **Performance**: Benchmark critical paths

**Local CI Simulation:**

```bash
# Run the full CI suite locally
make ci

# Or run individual components
make test
make lint
make security-check
make docs-build
```

## Sample Configuration

Here's a complete sample configuration file (`config/config.yaml`):

```yaml
# MOM Configuration File
# Copy this to config/config.yaml and customize as needed

# Database Configuration
database:
  type: "sqlite"  # Options: sqlite, postgresql, mysql
  host: "localhost"
  port: 5432
  name: "mom_db"
  user: "mom_user"
  password: "secure_password"
  
  # SQLite specific (when type: sqlite)
  path: "data/mom.db"
  
  # Connection pool settings
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30

# Logging Configuration
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "logs/mom.log"
  max_size_mb: 100
  backup_count: 5
  
  # Component-specific logging levels
  loggers:
    "mom.core": "DEBUG"
    "mom.api": "INFO"
    "mom.database": "WARNING"

# API Configuration
api:
  host: "0.0.0.0"
  port: 8000
  debug: false
  
  # Security settings
  secret_key: "your-secret-key-here"
  access_token_expire_minutes: 30
  
  # CORS settings
  cors:
    origins: ["http://localhost:3000", "http://localhost:8501"]
    methods: ["GET", "POST", "PUT", "DELETE"]
    headers: ["*"]

# Streamlit Configuration
streamlit:
  title: "MOM - Modular Object Management"
  theme:
    primary_color: "#FF6B6B"
    background_color: "#FFFFFF"
    secondary_background_color: "#F0F2F6"
    text_color: "#262730"
  
  # Page settings
  page_config:
    layout: "wide"
    sidebar_state: "expanded"
    menu_items:
      "Get Help": "https://github.com/dhanvina/mom/issues"
      "About": "MOM v1.0.0 - Modular Object Management System"

# Object Management Settings
objects:
  # Default object types
  types:
    - "module"
    - "component"
    - "service"
    - "resource"
  
  # Validation rules
  validation:
    name_pattern: "^[a-zA-Z0-9_-]+$"
    max_name_length: 100
    required_fields: ["name", "type"]
  
  # Storage settings
  storage:
    base_path: "data/objects"
    backup_enabled: true
    backup_interval_hours: 24

# Performance Settings
performance:
  cache:
    enabled: true
    ttl_seconds: 3600
    max_size: 1000
  
  # Pagination
  pagination:
    default_page_size: 50
    max_page_size: 1000
  
  # Background tasks
  tasks:
    cleanup_interval_hours: 6
    max_concurrent_tasks: 5

# Monitoring and Metrics
monitoring:
  enabled: true
  metrics_endpoint: "/metrics"
  health_check_endpoint: "/health"
  
  # Prometheus settings
  prometheus:
    enabled: false
    port: 8001
    
  # Custom metrics
  custom_metrics:
    - "object_creation_rate"
    - "api_response_time"
    - "database_query_duration"

# Feature Flags
features:
  experimental_api: false
  advanced_search: true
  bulk_operations: true
  real_time_updates: false
  audit_logging: true
```

## System Flow Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   User Input    │───▶│   CLI / UI      │───▶│   Core Engine   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        ▼
                                │                ┌─────────────────┐
                                │                │                 │
                                │                │  Object Manager │
                                │                │                 │
                                │                └─────────────────┘
                                │                        │
                                │                        ▼
                                │                ┌─────────────────┐
                                │                │                 │
                                │                │   Validation    │
                                │                │    Engine       │
                                │                │                 │
                                │                └─────────────────┘
                                │                        │
                                │                        ▼
                                │                ┌─────────────────┐
                                │                │                 │
                                └───────────────▶│   Database      │
                                                 │   Layer         │
                                                 │                 │
                                                 └─────────────────┘
                                                         │
                                                         ▼
                                                 ┌─────────────────┐
                                                 │                 │
                                                 │   Storage       │
                                                 │   (SQLite/      │
                                                 │   PostgreSQL)   │
                                                 │                 │
                                                 └─────────────────┘

Data Flow:
1. User interacts via CLI or Streamlit UI
2. Commands processed by Core Engine
3. Object Manager handles CRUD operations
4. Validation Engine ensures data integrity
5. Database Layer manages persistence
6. Results returned to user interface

Key Components:
• CLI: Command-line interface for programmatic access
• Streamlit UI: Web-based graphical interface
• Core Engine: Central processing and business logic
• Object Manager: Handles object lifecycle operations
• Validation Engine: Ensures data consistency and rules
• Database Layer: Abstraction for different storage backends
```

## Next Steps

After completing this quickstart guide:

1. **Read the Architecture Documentation**: Learn about system design and components
   - [Architecture Overview](architecture.md)
   - [API Documentation](api.md)
   - [Database Schema](database.md)

2. **Explore Advanced Features**:
   - Custom object types and validation rules
   - Plugin development and extensions
   - Performance optimization techniques
   - Advanced search and filtering

3. **Contributing to the Project**:
   - Check the [Contributing Guidelines](../CONTRIBUTING.md)
   - Review [Code Style Guide](code-style.md)
   - Browse [Open Issues](https://github.com/dhanvina/mom/issues)
   - Submit your first Pull Request

4. **Community and Support**:
   - Join discussions in [GitHub Discussions](https://github.com/dhanvina/mom/discussions)
   - Report bugs via [GitHub Issues](https://github.com/dhanvina/mom/issues)
   - Follow updates in the [Changelog](../CHANGELOG.md)

5. **Deployment and Production**:
   - [Production Deployment Guide](deployment.md)
   - [Monitoring and Observability](monitoring.md)
   - [Security Best Practices](security.md)

---

**Happy coding with MOM!** 🚀

For questions or support, please reach out via [GitHub Issues](https://github.com/dhanvina/mom/issues) or check our [FAQ](faq.md).
