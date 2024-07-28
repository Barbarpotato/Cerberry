# Gunakan base image Python 3.11.5
FROM python:3.13.0b2

# Set working directory di dalam container
WORKDIR /app

# Copy file requirements.txt dan install dependencies
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy seluruh kode aplikasi ke dalam container
COPY . .

# Menentukan port yang akan di-expose
EXPOSE 5000

# Command untuk menjalankan aplikasi Flask
CMD ["flask", "run"]
