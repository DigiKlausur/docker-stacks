#!/bin/bash
# Usage: ./build-and-deploy-hub.sh --registry <registry_url> --deployment <deployment_name> [--publish] [--verbose]
# Deployment name can be development, staging, or production

# Usage function
usage() {
    echo "Usage: $0 -r <registry> -d <deployment_name> [-p] [-v]"
    echo "  -r, --registry     Docker registry URL"
    echo "  -d, --deployment   Deployment name (development, production). Default is development."
    echo "  -p, --publish      Publish the image to the registry"
    echo "  -v, --verbose      Enable verbose output"
}

# Parse command-line arguments
DEPLOYMENT="development"
PUBLISH=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -d|--deployment)
            DEPLOYMENT="$2"
            shift 2
            ;;
        -p|--publish)
            PUBLISH=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            usage
            exit 1
            ;;
    esac
done

# Validate required parameters (registry)
if [ -z "$REGISTRY" ]; then
    echo "Error: --registry is a required argument."
    usage
    exit 1
fi

# Validate deployment name
if [[ "$DEPLOYMENT" != "development" && "$DEPLOYMENT" != "production" ]]; then
    echo "Error: --deployment must be one of development, or production."
    usage
    exit 1
fi

# Save current path
SCRIPT_PATH=$(pwd)

DATE=$(date +"%Y-%m-%d")

# Function to call the build-and-deploy-single-image.sh script
call_build_and_deploy() {
    local IMAGE_PATH="$1"
    local IMAGE_NAME="$2"

    # Determine tags based on deployment type
    if [[ "$DEPLOYMENT" == "production" ]]; then
        TAGS=("latest" "$DATE")
    elif [[ "$DEPLOYMENT" == "development" ]]; then
        TAGS=("dev" "dev-$DATE")
    fi

    # Make sure we are in the correct directory
    cd "$SCRIPT_PATH" || exit 1

    # Construct the command
    CMD="bash ci/build-and-deploy-single-image.sh -i \"$IMAGE_PATH\" -r \"$REGISTRY\" -n \"$IMAGE_NAME\""
    for TAG in "${TAGS[@]}"; do
        CMD+=" -t \"$TAG\""
    done

    # Add optional flags
    if [ "$PUBLISH" = true ]; then
        CMD+=" -p"
    fi
    if [ "$VERBOSE" = true ]; then
        CMD+=" -v"
    fi

    # Execute the command and check if it fails
    echo "Executing command: $CMD"
    eval "$CMD"
    if [ $? -ne 0 ]; then
        echo "Build and deploy failed for image: $IMAGE_NAME. Exiting."
        exit 1
    fi
}

# Build the images by iterating through the directories
function build_k8s_hub {
    cd hub
    for dir in */; do
        if [ -d "$dir" ]; then
            K8S_HUB_IMAGE_DIR="${dir%/}"
            echo "Building K8S hub image for $K8S_HUB_IMAGE_DIR"
            K8S_VERSION=$K8S_HUB_IMAGE_DIR
            IMAGE_NAME="k8s-hub-$K8S_VERSION"
            IMAGE_PATH="hub/$K8S_HUB_IMAGE_DIR"  # Ensure this is the correct image path
            call_build_and_deploy "$IMAGE_PATH" "$IMAGE_NAME"
            # Move back to the hub path for the next iteration
            cd $SCRIPT_PATH/hub || exit 1

        fi
    done
}

# Main script logic
echo "Current date: $DATE"
echo "Deployment: $DEPLOYMENT"
echo "Registry: $REGISTRY"
build_k8s_hub
