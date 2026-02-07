#!/bin/bash
# AWS Profile Manager - Easily switch between AWS profiles and view credentials
# Usage: ./aws-profile-manager.sh [list|switch|default|info]

set -e

COLOR_GREEN='\033[0;32m'
COLOR_BLUE='\033[0;34m'
COLOR_RED='\033[0;31m'
COLOR_YELLOW='\033[1;33m'
NC='\033[0m' # No Color

AWS_CREDS_FILE="${HOME}/.aws/credentials"
AWS_CONFIG_FILE="${HOME}/.aws/config"

print_header() {
    echo -e "${COLOR_BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${COLOR_GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${COLOR_RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${COLOR_YELLOW}⚠ $1${NC}"
}

list_profiles() {
    print_header "Available AWS Profiles"
    
    if [ ! -f "$AWS_CREDS_FILE" ]; then
        print_error "Credentials file not found: $AWS_CREDS_FILE"
        return 1
    fi
    
    profiles=$(grep -E '^\[.*\]$' "$AWS_CREDS_FILE" | sed 's/\[//g;s/\]//g')
    
    if [ -z "$profiles" ]; then
        print_warning "No profiles found"
        return 1
    fi
    
    current_profile="${AWS_PROFILE:-default}"
    
    while IFS= read -r profile; do
        if [ "$profile" = "$current_profile" ]; then
            echo -e "${COLOR_GREEN}→ $profile${NC}"
        else
            echo "  $profile"
        fi
    done <<< "$profiles"
}

switch_profile() {
    local target_profile="$1"
    
    if [ -z "$target_profile" ]; then
        print_error "Profile name required"
        return 1
    fi
    
    # Verify profile exists
    if ! grep -q "^\[$target_profile\]$" "$AWS_CREDS_FILE"; then
        print_error "Profile '$target_profile' not found"
        return 1
    fi
    
    export AWS_PROFILE="$target_profile"
    print_success "Switched to profile: $target_profile"
    
    # Verify connection
    if aws sts get-caller-identity &>/dev/null; then
        print_success "Profile authenticated successfully"
    else
        print_warning "Unable to verify profile authentication"
    fi
}

show_profile_info() {
    local profile="${1:-${AWS_PROFILE:-default}}"
    
    print_header "Profile: $profile"
    
    if ! grep -q "^\[$profile\]$" "$AWS_CREDS_FILE"; then
        print_error "Profile '$profile' not found"
        return 1
    fi
    
    echo -e "\n${COLOR_BLUE}Credentials:${NC}"
    awk "/^\[$profile\]$/,/^$/" "$AWS_CREDS_FILE" | grep -v "^\[$" | grep -v "^$"
    
    if [ -f "$AWS_CONFIG_FILE" ]; then
        echo -e "\n${COLOR_BLUE}Configuration:${NC}"
        awk "/^\[profile $profile\]|^\[$profile\]/,/^$/" "$AWS_CONFIG_FILE" | grep -v "^\[" | grep -v "^$"
    fi
    
    echo -e "\n${COLOR_BLUE}Identity:${NC}"
    if AWS_PROFILE="$profile" aws sts get-caller-identity 2>/dev/null; then
        print_success "Profile is valid"
    else
        print_error "Profile authentication failed"
    fi
}

set_default_profile() {
    local profile="$1"
    
    if [ -z "$profile" ]; then
        print_error "Profile name required"
        return 1
    fi
    
    if ! grep -q "^\[$profile\]$" "$AWS_CREDS_FILE"; then
        print_error "Profile '$profile' not found"
        return 1
    fi
    
    export AWS_PROFILE="$profile"
    echo "export AWS_PROFILE='$profile'" >> ~/.bashrc
    echo "export AWS_PROFILE='$profile'" >> ~/.zshrc
    
    print_success "Default profile set to: $profile"
    print_warning "Please restart your shell or run: source ~/.bashrc"
}

case "${1:-list}" in
    list)
        list_profiles
        ;;
    switch)
        switch_profile "$2"
        ;;
    info)
        show_profile_info "$2"
        ;;
    default)
        set_default_profile "$2"
        ;;
    *)
        echo "Usage: $0 {list|switch|default|info} [profile_name]"
        exit 1
        ;;
esac
