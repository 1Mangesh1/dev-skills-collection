#!/usr/bin/env bash
# S3 Bucket Manager
# Manage AWS S3 buckets with common operations

create_bucket() {
    local bucket_name="$1"
    local region="${2:-us-east-1}"
    
    aws s3api create-bucket \
        --bucket "$bucket_name" \
        --region "$region" \
        --create-bucket-configuration LocationConstraint="$region"
    
    echo "Bucket $bucket_name created in $region"
}

upload_files() {
    local bucket="$1"
    local local_path="$2"
    
    aws s3 sync "$local_path" "s3://$bucket/" \
        --exclude "*.git/*" \
        --exclude "node_modules/*"
    
    echo "Files uploaded to s3://$bucket/"
}

list_buckets() {
    aws s3api list-buckets --query 'Buckets[].{Name:Name,Created:CreationDate}' --output table
}

# Usage
create_bucket "my-app-bucket"
upload_files "my-app-bucket" "./dist"
list_buckets
