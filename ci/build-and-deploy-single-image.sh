#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -i, --image-path     Path to the directory containing the Dockerfile"
    echo "  -r, --registry       Container registry (e.g., ghcr.io/digiklausur/docker-stacks)"
    echo "  -n, --name           Image name"
    echo "  -t, --tag            Tag for the image (can be used multiple times, e.g., -t latest -t 2025-03-10)"
    echo "  -p, --publish        Push the image after building (no value needed)"
    echo "  -v, --verbose        Show full Docker build output (adds --progress=plain)"
    echo "  -b, --build-arg      Optional build argument (can be used multiple times, e.g., -b KEY=VALUE)"
    echo ""
    echo "Example:"
    echo "  $0 -i ./path -r ghcr.io/your-registry -n my-image -t latest -p -v -b VERSION=1.0 -b COMMIT=abc123"
}

# Parse command-line arguments
TAGS=()
BUILD_ARGS=()
PUBLISH=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--image-path)
            IMAGE_PATH="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            if [[ -n $2 && $2 != -* ]]; then
                TAGS+=("$2")
                shift 2
            else
                echo "Error: --tag requires a value"
                exit 1
            fi
            ;;
        -p|--publish)
            PUBLISH=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -b|--build-arg)
            if [[ -n $2 && $2 != -* ]]; then
                BUILD_ARGS+=("--build-arg" "$2")
                shift 2
            else
                echo "Error: --build-arg requires a value"
                exit 1
            fi
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$IMAGE_PATH" ] || [ -z "$REGISTRY" ] || [ -z "$IMAGE_NAME" ] || [ ${#TAGS[@]} -eq 0 ]; then
    usage
    exit 1
fi

# Check if the Dockerfile exists
if [ ! -f "$IMAGE_PATH/Dockerfile" ]; then
    echo "Dockerfile not found at $IMAGE_PATH/Dockerfile"
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
BUILD_COMMAND="docker build ${BUILD_ARGS[@]} -f \"$IMAGE_PATH/Dockerfile\""

# Add tags
for tag in "${TAGS[@]}"; do
    BUILD_COMMAND+=" -t ${REGISTRY}/${IMAGE_NAME}:${tag}"
done

# Add context path
BUILD_COMMAND+=" \"$IMAGE_PATH\""

# Add verbose flag if enabled
if [ "$VERBOSE" = true ]; then
    BUILD_COMMAND+=" --progress=plain"
fi

# Show the full command (debugging)
echo "Executing command: $BUILD_COMMAND"

# Execute
if ! eval "$BUILD_COMMAND"; then
    echo "Failed to build Docker image"
    exit 1
fi

# Push the image if flag was set
if [ "$PUBLISH" = true ]; then
    echo "Pushing Docker image..."
    for tag in "${TAGS[@]}"; do
        if ! docker push "${REGISTRY}/${IMAGE_NAME}:${tag}" 2>&1; then
            echo "Failed to push Docker image with tag ${tag}"
            exit 1
        fi
    done
fi

echo "Done!"
