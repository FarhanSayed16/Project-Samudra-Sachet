#!/bin/bash

# Project Samudra Sachet - Deployment Script
# This script handles the deployment of the entire application stack

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="samudra-sachet"
ENVIRONMENT=${1:-production}
DOCKER_COMPOSE_FILE="docker-compose.prod.yml"
BACKUP_DIR="./backups"
LOG_FILE="./deployment.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed. Please install Docker Compose first."
    fi
    
    success "Docker and Docker Compose are installed"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        warning ".env file not found. Creating from template..."
        if [ -f "env.template" ]; then
            cp env.template .env
            warning "Please edit .env file with your configuration before running deployment again"
            exit 1
        else
            error ".env file not found and no template available"
        fi
    fi
    
    success ".env file found"
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$BACKUP_DIR"
    mkdir -p "./nginx/ssl"
    mkdir -p "./monitoring/grafana/dashboards"
    mkdir -p "./monitoring/grafana/datasources"
    mkdir -p "./monitoring/logstash"
    
    success "Directories created"
}

# Backup existing data
backup_data() {
    log "Creating backup of existing data..."
    
    BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    
    if [ -d "./data" ]; then
        tar -czf "$BACKUP_FILE" ./data
        success "Backup created: $BACKUP_FILE"
    else
        warning "No existing data directory found"
    fi
}

# Build and deploy services
deploy_services() {
    log "Building and deploying services..."
    
    # Pull latest images
    docker-compose -f "$DOCKER_COMPOSE_FILE" pull
    
    # Build custom images
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    # Stop existing services
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    # Start services
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    success "Services deployed successfully"
}

# Wait for services to be healthy
wait_for_services() {
    log "Waiting for services to be healthy..."
    
    # Wait for database
    log "Waiting for database..."
    timeout 60 bash -c 'until docker-compose -f '"$DOCKER_COMPOSE_FILE"' exec -T postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB; do sleep 2; done'
    
    # Wait for Redis
    log "Waiting for Redis..."
    timeout 30 bash -c 'until docker-compose -f '"$DOCKER_COMPOSE_FILE"' exec -T redis redis-cli ping; do sleep 2; done'
    
    # Wait for backend
    log "Waiting for backend..."
    timeout 60 bash -c 'until curl -f http://localhost:8000/health; do sleep 2; done'
    
    # Wait for frontend
    log "Waiting for frontend..."
    timeout 60 bash -c 'until curl -f http://localhost:3000; do sleep 2; done'
    
    success "All services are healthy"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T backend alembic upgrade head
    
    success "Database migrations completed"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    if [ ! -f "./nginx/ssl/cert.pem" ] || [ ! -f "./nginx/ssl/key.pem" ]; then
        warning "SSL certificates not found. Please add them to ./nginx/ssl/ directory"
        warning "For development, you can generate self-signed certificates:"
        warning "openssl req -x509 -newkey rsa:4096 -keyout ./nginx/ssl/key.pem -out ./nginx/ssl/cert.pem -days 365 -nodes"
    else
        success "SSL certificates found"
    fi
}

# Run health checks
health_check() {
    log "Running health checks..."
    
    # Check backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        success "Backend is healthy"
    else
        error "Backend health check failed"
    fi
    
    # Check frontend health
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        success "Frontend is healthy"
    else
        error "Frontend health check failed"
    fi
    
    # Check database connection
    if docker-compose -f "$DOCKER_COMPOSE_FILE" exec -T postgres pg_isready -U $POSTGRES_USER -d $POSTGRES_DB > /dev/null 2>&1; then
        success "Database is healthy"
    else
        error "Database health check failed"
    fi
    
    success "All health checks passed"
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    
    echo ""
    echo "Services:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps
    
    echo ""
    echo "Service URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "  Grafana: http://localhost:3001"
    echo "  Prometheus: http://localhost:9090"
    echo "  Kibana: http://localhost:5601"
    
    echo ""
    echo "Logs:"
    echo "  View logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f"
    echo "  View specific service logs: docker-compose -f $DOCKER_COMPOSE_FILE logs -f [service_name]"
    
    echo ""
    echo "Management:"
    echo "  Stop services: docker-compose -f $DOCKER_COMPOSE_FILE down"
    echo "  Restart services: docker-compose -f $DOCKER_COMPOSE_FILE restart"
    echo "  Update services: docker-compose -f $DOCKER_COMPOSE_FILE pull && docker-compose -f $DOCKER_COMPOSE_FILE up -d"
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    success "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting deployment for environment: $ENVIRONMENT"
    
    check_docker
    check_env
    create_directories
    backup_data
    setup_ssl
    deploy_services
    wait_for_services
    run_migrations
    health_check
    cleanup
    show_status
    
    success "Deployment completed successfully!"
    log "Deployment log saved to: $LOG_FILE"
}

# Handle script interruption
trap 'error "Deployment interrupted"' INT TERM

# Run main function
main "$@"

