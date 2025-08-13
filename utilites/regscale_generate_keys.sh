#!/bin/bash

# RegScale Key Generator
# Generates 2 unique 256-bit (32 character) keys
# Compatible with RHEL, Ubuntu, and WSL

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate a 256-bit key using OpenSSL
generate_key_openssl() {
    openssl rand -hex 16 2>/dev/null
}

# Function to generate a 256-bit key using /dev/urandom (fallback)
generate_key_urandom() {
    head -c 16 /dev/urandom | xxd -p -c 16 2>/dev/null || \
    head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n' | cut -c1-32
}

# Function to generate a key with fallback methods
generate_key() {
    local key=""
    
    # Try OpenSSL first
    if command_exists openssl; then
        key=$(generate_key_openssl)
        if [ $? -eq 0 ] && [ ${#key} -eq 32 ]; then
            echo "$key"
            return 0
        fi
    fi
    
    # Fallback to /dev/urandom
    if [ -r /dev/urandom ]; then
        key=$(generate_key_urandom)
        if [ $? -eq 0 ] && [ ${#key} -eq 32 ]; then
            echo "$key"
            return 0
        fi
    fi
    
    return 1
}

# Main function
main() {
    print_status "RegScale Key Generator"
    print_status "Generating RegScale JWTSecretKey and EncryptionKey..."
    echo
    
    # Check for required tools
    if ! command_exists openssl && [ ! -r /dev/urandom ]; then
        print_error "Neither OpenSSL nor /dev/urandom is available"
        print_error "Please install OpenSSL or ensure /dev/urandom is accessible"
        exit 1
    fi
    
    # Generate first key
    print_status "Generating JWTSecretKey..."
    key1=$(generate_key)
    if [ $? -ne 0 ]; then
        print_error "Failed to generate JWTSecretKey"
        exit 1
    fi
    print_success "JWTSecretKey generated successfully"
    
    # Generate second key
    print_status "Generating EncryptionKey..."
    key2=$(generate_key)
    if [ $? -ne 0 ]; then
        print_error "Failed to generate EncryptionKey"
        exit 1
    fi
    
    # Ensure keys are different
    if [ "$key1" = "$key2" ]; then
        print_warning "Generated keys are identical, regenerating EncryptionKey..."
        key2=$(generate_key)
        if [ $? -ne 0 ]; then
            print_error "Failed to regenerate EncryptionKey"
            exit 1
        fi
    fi
    
    print_success "EncryptionKey generated successfully"
    echo
    
    # Display results
    print_success "Generated Keys:"
    echo "JWTSecretKey: $key1"
    echo "EncryptionKey: $key2"
    echo
    
    # Verify key lengths
    if [ ${#key1} -eq 32 ] && [ ${#key2} -eq 32 ]; then
        print_success "Both keys are 256-bit (32 characters) as required"
    else
        print_warning "Key length verification failed"
        print_warning "JWTSecretKey length: ${#key1} characters"
        print_warning "EncryptionKey length: ${#key2} characters"
    fi
    echo
    
    # Usage instructions
    print_status "Usage Instructions:"
    echo "1. Copy the keys above for use in your regscale.env file"
    echo "2. Store keys securely and do not share them"
    echo "3. Each key is 256-bit (32 hexadecimal characters)"
    echo "4. Keys are cryptographically secure random values"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
