#!/usr/bin/env python3
"""
Test script to verify global exception handling
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from fastapi.testclient import TestClient
from app.main import app
from app.shared.exceptions.exceptions import AuthenticationError, ValidationError

client = TestClient(app)

# Test the global exception handler by raising an exception in a route
@app.get("/test-auth-error")
def test_auth_error():
    raise AuthenticationError("Test authentication error", "TEST_AUTH")

@app.get("/test-validation-error")
def test_validation_error():
    raise ValidationError("Test validation error", "TEST_VALIDATION")

if __name__ == "__main__":
    # Test authentication error
    response = client.get("/test-auth-error")
    print("Auth Error Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Test validation error
    response = client.get("/test-validation-error")
    print("Validation Error Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    print("Exception handling test completed!")