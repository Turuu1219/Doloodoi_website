FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy all project files
COPY . .

# Ensure upload dirs exist
RUN mkdir -p frontend/static/uploads/{logo,school,director,teachers,news,gallery}

EXPOSE 5000

CMD ["python", "-m", "backend.app"]
