#!/bin/bash

# PodTranslate Deployment Script
# Deploys all services to Kubernetes cluster

set -e

echo "🚀 PodTranslate Deployment Script"
echo "=================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found. Please install kubectl."
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        print_error "docker not found. Please install docker."
        exit 1
    fi

    print_success "Prerequisites check passed"
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."

    services=("api-gateway" "audio-processing" "distribution" "analytics" "ai-tools")

    for service in "${services[@]}"; do
        print_info "Building $service..."
        docker build -t podtranslate/$service:latest ./services/$service
        print_success "$service image built"
    done
}

# Push images to registry
push_images() {
    REGISTRY=${1:-""}

    if [ -z "$REGISTRY" ]; then
        print_info "No registry specified, skipping push"
        return
    fi

    print_info "Pushing images to $REGISTRY..."

    services=("api-gateway" "audio-processing" "distribution" "analytics" "ai-tools")

    for service in "${services[@]}"; do
        print_info "Pushing $service..."
        docker tag podtranslate/$service:latest $REGISTRY/podtranslate/$service:latest
        docker push $REGISTRY/podtranslate/$service:latest
        print_success "$service pushed"
    done
}

# Deploy to Kubernetes
deploy_k8s() {
    print_info "Deploying to Kubernetes..."

    # Create namespace
    kubectl apply -f infrastructure/kubernetes/00-namespace.yaml
    print_success "Namespace created"

    # Apply configurations
    print_info "Applying configurations..."
    kubectl apply -f infrastructure/kubernetes/

    print_success "All resources deployed"
}

# Wait for rollout
wait_for_rollout() {
    print_info "Waiting for deployments to be ready..."

    deployments=("api-gateway" "audio-processing" "distribution" "analytics" "ai-tools")

    for deployment in "${deployments[@]}"; do
        print_info "Waiting for $deployment..."
        kubectl rollout status deployment/$deployment -n podtranslate --timeout=5m
        print_success "$deployment is ready"
    done
}

# Run database migrations
run_migrations() {
    print_info "Running database migrations..."

    # Create a job to run migrations
    kubectl run migrations --image=podtranslate/api-gateway:latest \
        --restart=Never \
        --namespace=podtranslate \
        --command -- alembic upgrade head

    # Wait for job to complete
    kubectl wait --for=condition=complete --timeout=5m job/migrations -n podtranslate

    print_success "Migrations completed"
}

# Check service health
check_health() {
    print_info "Checking service health..."

    # Get API Gateway external IP
    EXTERNAL_IP=$(kubectl get svc api-gateway -n podtranslate -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

    if [ -z "$EXTERNAL_IP" ]; then
        print_error "Could not get external IP"
        return
    fi

    print_info "API Gateway: http://$EXTERNAL_IP"

    # Check health endpoint
    if curl -sf "http://$EXTERNAL_IP/api/v1/health" > /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
    fi
}

# Main deployment flow
main() {
    echo ""
    print_info "Starting deployment..."
    echo ""

    # Parse arguments
    REGISTRY=""
    SKIP_BUILD=false
    SKIP_PUSH=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --registry)
                REGISTRY="$2"
                shift 2
                ;;
            --skip-build)
                SKIP_BUILD=true
                shift
                ;;
            --skip-push)
                SKIP_PUSH=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Run deployment steps
    check_prerequisites

    if [ "$SKIP_BUILD" = false ]; then
        build_images
    fi

    if [ "$SKIP_PUSH" = false ] && [ -n "$REGISTRY" ]; then
        push_images "$REGISTRY"
    fi

    deploy_k8s
    wait_for_rollout
    run_migrations
    check_health

    echo ""
    print_success "Deployment completed successfully! 🎉"
    echo ""
    print_info "Next steps:"
    echo "  1. Configure DNS for your domain"
    echo "  2. Set up SSL certificates"
    echo "  3. Configure monitoring alerts"
    echo "  4. Run load tests"
    echo ""
}

# Run main function
main "$@"
