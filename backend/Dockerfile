FROM python:3.12-alpine

# Install system dependencies for WeasyPrint, Django, and PostgreSQL
RUN apk add --no-cache \
    # PostgreSQL client and build dependencies
    postgresql-client \
    postgresql-dev \
    # Build tools
    gcc \
    musl-dev \
    linux-headers \
    # WeasyPrint dependencies for PDF generation
    cairo \
    cairo-dev \
    pango \
    pango-dev \
    gdk-pixbuf \
    gdk-pixbuf-dev \
    libffi-dev \
    shared-mime-info \
    # Fonts for PDF rendering
    ttf-dejavu \
    ttf-droid \
    ttf-freefont \
    ttf-liberation \
    fontconfig

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "trust_account_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
