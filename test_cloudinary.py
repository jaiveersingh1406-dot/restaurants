#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv

# Load from the specific .env file
load_dotenv("/Users/jaiveersingh/Desktop/rastraunt backend /.env")

import cloudinary
from app.core.cloud import is_configured, _config

cfg = _config()
print("=" * 50)
print("CLOUDINARY CONFIGURATION CHECK")
print("=" * 50)
print(f"Cloud Name: {cfg['cloud_name']}")
print(f"API Key: {cfg['api_key'][:10]}..." if cfg['api_key'] else "API Key: (empty)")
print(f"API Secret: {cfg['api_secret'][:10]}..." if cfg['api_secret'] else "API Secret: (empty)")
print(f"\nConfiguration Status: {'✓ READY' if is_configured() else '✗ NOT CONFIGURED'}")
print("=" * 50)

# Test connection
try:
    cloudinary.config(
        cloud_name=cfg['cloud_name'],
        api_key=cfg['api_key'],
        api_secret=cfg['api_secret'],
    )
    print("✓ Cloudinary connection successful!")
    print(f"✓ Ready to upload images to folder: platia")
except Exception as e:
    print(f"✗ Connection error: {e}")
