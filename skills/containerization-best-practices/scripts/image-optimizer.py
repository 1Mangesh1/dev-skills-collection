#!/usr/bin/env python3
"""
Image Optimizer - Generate optimized Dockerfiles with multi-stage builds.
Produces smaller, more secure container images.
"""

import json
import subprocess
from typing import Dict

class ImageOptimizer:
    """Optimize Docker images."""
    
    def generate_optimized_dockerfile(self, app_type: str, base_image: str = None) -> str:
        """Generate an optimized Dockerfile."""
        
        if app_type == 'python':
            return self.generate_python_dockerfile(base_image)
        elif app_type == 'nodejs':
            return self.generate_nodejs_dockerfile(base_image)
        elif app_type == 'rust':
            return self.generate_rust_dockerfile(base_image)
        else:
            return self.generate_generic_dockerfile(base_image)
    
    def generate_python_dockerfile(self, base_image: str = None) -> str:
        """Generate optimized Python Dockerfile."""
        if base_image is None:
            base_image = 'python:3.11-slim'
        
        return f'''# Multi-stage build for optimal image size
FROM {base_image} as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Final stage
FROM {base_image}

WORKDIR /app

# Create non-root user
RUN useradd -r -u 1001 appuser

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

# Install dependencies and clean
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy application code
COPY --chown=appuser:appuser . .

# Security: Run as non-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Metadata
LABEL maintainer="team@example.com"
LABEL version="1.0"

# Run application
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
'''
    
    def generate_nodejs_dockerfile(self, base_image: str = None) -> str:
        """Generate optimized Node.js Dockerfile."""
        if base_image is None:
            base_image = 'node:18-alpine'
        
        return f'''# Multi-stage build for Node.js
FROM {base_image} as builder

WORKDIR /build

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \\
    npm cache clean --force

# Build application (if needed)
COPY . .
RUN npm run build 2>/dev/null || true

# Final stage
FROM {base_image}

WORKDIR /app

# Create non-root user
RUN addgroup -S appuser && adduser -S appuser -G appuser

# Copy artifacts from builder
COPY --from=builder --chown=appuser:appuser /build/node_modules ./node_modules
COPY --from=builder --chown=appuser:appuser /build . .

# Security: Run as non-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \\
    CMD wget --quiet --tries=1 --spider http://localhost:3000/health || exit 1

# Metadata
LABEL maintainer="team@example.com"

# Expose port
EXPOSE 3000

# Run application
CMD ["node", "server.js"]
'''
    
    def generate_rust_dockerfile(self, base_image: str = None) -> str:
        """Generate optimized Rust Dockerfile."""
        return '''# Multi-stage build for Rust - minimal binary size
FROM rust:1.74-slim as builder

WORKDIR /build

# Copy source
COPY . .

# Build release binary
RUN cargo build --release --target x86_64-unknown-linux-musl

# Final stage - uses scratch for minimal image
FROM scratch

COPY --from=builder /build/target/x86_64-unknown-linux-musl/release/app /app

# Metadata
LABEL maintainer="team@example.com"

HEALTHCHECK --interval=30s CMD ["/app", "health"]
EXPOSE 8000

ENTRYPOINT ["/app"]
'''
    
    def generate_generic_dockerfile(self, base_image: str = None) -> str:
        """Generate generic optimized Dockerfile."""
        if base_image is None:
            base_image = 'ubuntu:22.04'
        
        return f'''# Optimized multi-stage Dockerfile
FROM {base_image} as builder

WORKDIR /build

# Update and install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \\
    git \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy and build
COPY . .
RUN ./build.sh

# Final stage
FROM {base_image}

WORKDIR /app

# Create non-root user
RUN useradd -r -u 1001 appuser

# Copy only necessary artifacts
COPY --from=builder --chown=appuser:appuser /build/dist . 

USER appuser

HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health || exit 1

LABEL maintainer="team@example.com"

EXPOSE 8000
ENTRYPOINT ["./app"]
'''
    
    def analyze_image_size(self, image_name: str) -> Dict:
        """Analyze Docker image size."""
        
        try:
            result = subprocess.run(
                ['docker', 'inspect', '--format={{json .Size}}', image_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                size_bytes = int(result.stdout.strip())
                return {
                    'image': image_name,
                    'size_bytes': size_bytes,
                    'size_mb': round(size_bytes / (1024*1024), 2),
                    'size_gb': round(size_bytes / (1024**3), 2)
                }
        except Exception as e:
            return {'error': str(e)}
        
        return {}
    
    def generate_optimization_report(self, current_size: float, optimized_size: float) -> Dict:
        """Generate size optimization report."""
        reduction = current_size - optimized_size
        reduction_percent = (reduction / current_size) * 100 if current_size > 0 else 0
        
        return {
            'current_size_mb': round(current_size, 2),
            'optimized_size_mb': round(optimized_size, 2),
            'reduction_mb': round(reduction, 2),
            'reduction_percent': round(reduction_percent, 1),
            'optimization_techniques': [
                'Multi-stage builds',
                'Use slim/alpine base images',
                'Minimize layers',
                'Remove build dependencies',
                'Use .dockerignore to exclude unnecessary files',
                'Combine RUN commands'
            ]
        }

def main():
    optimizer = ImageOptimizer()
    
    # Generate optimized Docker files
    for app_type in ['python', 'nodejs', 'rust']:
        dockerfile = optimizer.generate_optimized_dockerfile(app_type)
        print(f"# Optimized Dockerfile for {app_type}")
        print(dockerfile)
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
