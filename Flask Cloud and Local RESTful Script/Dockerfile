# Set the base image
FROM python:3.8

# Install the required packages
RUN pip install --no-cache-dir transformers==4.31.0 Flask==2.3.2 Flask-Cors==4.0.0 flask-talisman tensorflow==2.10.0
RUN pip install gunicorn

# Install a Rust compiler to use the tokenizers
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the Flask app code
COPY Flask_app_optimized.py /app/

# Copy the models
COPY NEW_mobile_distilBERT_optimized.tflite /app/
COPY mobile_portuguese_distilBERT_optimized.tflite /app/

# Set the working directory
WORKDIR /app

# Expose the necessary port
EXPOSE 80
EXPOSE 443

# Run the Flask app with Gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:80", "--certfile", "/etc/ssl/certs/fullchain.pem", "--keyfile", "/etc/ssl/certs/privkey.pem", "-b", "0.0.0.0:443", "Flask_app_optimized:app"]