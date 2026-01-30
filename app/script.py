"""
Integration Test Script for Forms API
Tests actual API endpoints against real database
"""
import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
# Replace with your actual Keycloak token or set to None if auth not enforced yet
AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJpZ0JPbUVaZHY1LXNYUV82ZmtFTlYwMjdvbkktX0FDRUdLVi1TX0JuMmNBIn0.eyJleHAiOjE3Njk1MjIwNDIsImlhdCI6MTc2OTUyMTc0MiwianRpIjoib25ydHJvOmI1NGQzNzdiLTZlM2UtOThhYy01Mzg4LTAwMWY2ZjBkYjQ3MyIsImlzcyI6Imh0dHA6Ly9rZXljbG9hazo4MDgwL3JlYWxtcy9teV9yZWFsbSIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiIyODVjOGE2MS0wMzM0LTQ0ZWYtOWFjZi1mMDMyZjFjMTVjZTUiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJmYXN0YXBpLWJhY2tlbmQiLCJzaWQiOiI1YjVkOGYyZC1mYThkLWNjNDUtMzMyZi01NmFlMWY0YmE4MDMiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6ODAwMCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1teV9yZWFsbSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJBd2FpcyBTaGFoemFkIiwicHJlZmVycmVkX3VzZXJuYW1lIjoidGVzdHVzZXIiLCJnaXZlbl9uYW1lIjoiQXdhaXMiLCJmYW1pbHlfbmFtZSI6IlNoYWh6YWQiLCJlbWFpbCI6ImF3YWlzQGVtYWlsLmNvbSJ9.Hw6Uda_ZSkupj_p7fdK2Ie6iwGSedyXDZiG7BLGkbyWPEi5sDYcgOORi_LFIUGEPcomTdBm6hY1NACdUv-m6yVrmYDpULcwsU8Mc1i4wgZaFpTcRvKad6ZoizeNomkmVIkVYiRSnGcu9v-x3Qq8W_ZUlTZE7yZ5mihlaDY0gXx-ohy3WLA__iC4k2a5Pehaoa_exAeFoNtIHyHeI_x-62u_Z9YOTgEwaXro1TC-ki3vDxsxu9OZvY0YiWiVlOX8KqfW7CFGv1FTk0Tn5TAFE1EP85Swvy6cuPHbDoKbq2uel4nUEeF9BXkASUmRZmzDJ_huj2GWJ0crYFKfotrp80Q"
class FormsAPITester:
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"
        
        self.created_resources = {
            "forms": [],
            "submissions": []
        }
    
    def log(self, message: str, emoji: str = "📝"):
        print(f"{emoji} {message}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None):
        """Make HTTP request and handle errors"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            
            # Log request
            print(f"\n{'='*60}")
            print(f"📤 {method} {endpoint}")
            if data:
                print(f"📦 Request Body: {json.dumps(data, indent=2)}")
            
            # Log response
            print(f"✅ Status: {response.status_code}")
            if response.status_code != 204:  # 204 has no content
                try:
                    print(f"📥 Response: {json.dumps(response.json(), indent=2)}")
                except:
                    print(f"📥 Response: {response.text}")
            
            response.raise_for_status()
            return response
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            raise
    
    def test_1_create_form(self):
        """Test 1: Create a donation tracking form with fields"""
        self.log("TEST 1: Creating form with fields", "🧪")
        
        form_data = {
            "name": "Donation Tracking Form",
            "description": "Track where Rs 150 donations go",
            "fields": [
                {
                    "label": "Donor Name",
                    "field_type": "text",
                    "required": "true",
                    "position": 0
                },
                {
                    "label": "Amount (Rs)",
                    "field_type": "number",
                    "required": "true",
                    "position": 1
                },
                {
                    "label": "Recipient",
                    "field_type": "text",
                    "required": "true",
                    "position": 2
                },
                {
                    "label": "Distribution Method",
                    "field_type": "select",
                    "required": "false",
                    "position": 3
                }
            ]
        }
        
        response = self.make_request("POST", "/forms/", form_data)
        form = response.json()
        
        self.created_resources["forms"].append(form["id"])
        
        assert form["name"] == "Donation Tracking Form"
        assert len(form["fields"]) == 4
        
        self.log(f"✅ Form created with ID: {form['id']}", "✅")
        return form
    
    def test_2_submit_form(self, form_id: str):
        """Test 2: Submit form data"""
        self.log("TEST 2: Submitting form data", "🧪")
        
        submission_data = {
            "form_id": form_id,
            "data": {
                "Donor Name": "Ahmed Khan",
                "Amount (Rs)": 150,
                "Recipient": "School Fund",
                "Distribution Method": "Direct Transfer"
            }
        }
        
        response = self.make_request("POST", f"/forms/{form_id}/submissions", submission_data)
        submission = response.json()
        
        self.created_resources["submissions"].append(submission["id"])
        
        # Verify snapshot was created
        assert submission["form_snapshot"] is not None
        assert "fields" in submission["form_snapshot"]
        assert len(submission["form_snapshot"]["fields"]) == 4
        
        self.log(f"✅ Submission created with ID: {submission['id']}", "✅")
        self.log(f"✅ Snapshot contains {len(submission['form_snapshot']['fields'])} fields", "✅")
        
        return submission
    
    def test_3_add_field(self, form_id: str):
        """Test 3: Add a new field to existing form"""
        self.log("TEST 3: Adding new field to form", "🧪")
        
        field_data = {
            "label": "Thank You Message",
            "field_type": "textarea",
            "required": "false",
            "position": 4
        }
        
        response = self.make_request("POST", f"/forms/{form_id}/fields", field_data)
        field = response.json()
        
        assert field["label"] == "Thank You Message"
        
        self.log(f"✅ Field added with ID: {field['id']}", "✅")
        return field
    
    def test_4_delete_field(self, form_id: str, field_label: str):
        """Test 4: Delete a field (soft delete)"""
        self.log(f"TEST 4: Deleting field '{field_label}'", "🧪")
        
        # Get all fields
        response = self.make_request("GET", f"/forms/{form_id}/fields")
        fields = response.json()
        
        # Find the field to delete
        field_to_delete = next((f for f in fields if f["label"] == field_label), None)
        
        if not field_to_delete:
            self.log(f"⚠️ Field '{field_label}' not found", "⚠️")
            return None
        
        # Delete it
        self.make_request("DELETE", f"/forms/{form_id}/fields/{field_to_delete['id']}")
        
        self.log(f"✅ Field '{field_label}' deleted (soft delete)", "✅")
        return field_to_delete["id"]
    
    def test_5_verify_snapshot_preservation(self, submission_id: str, deleted_field_label: str):
        """Test 5: CRITICAL - Verify old submission still has deleted field in snapshot"""
        self.log("TEST 5: Verifying snapshot preservation (CRITICAL)", "🧪")
        
        # Get the submission
        response = self.make_request("GET", f"/forms/submissions/{submission_id}")
        submission = response.json()
        
        # Check data still has the deleted field
        assert deleted_field_label in submission["data"], \
            f"❌ Data missing '{deleted_field_label}'"
        
        # Check snapshot still has the field definition
        snapshot_field_labels = [f["label"] for f in submission["form_snapshot"]["fields"]]
        assert deleted_field_label in snapshot_field_labels, \
            f"❌ Snapshot missing '{deleted_field_label}' field definition"
        
        self.log(f"✅ SNAPSHOT PRESERVED! Field '{deleted_field_label}' still in data", "🎉")
        self.log(f"✅ SNAPSHOT PRESERVED! Field '{deleted_field_label}' definition still in snapshot", "🎉")
        
        return True
    
    def test_6_list_submissions(self, form_id: str):
        """Test 6: List all submissions with pagination"""
        self.log("TEST 6: Listing submissions", "🧪")
        
        response = self.make_request("GET", f"/forms/{form_id}/submissions?skip=0&limit=10")
        submissions = response.json()
        
        assert isinstance(submissions, list)
        assert len(submissions) > 0
        
        self.log(f"✅ Found {len(submissions)} submissions", "✅")
        return submissions
    
    def test_7_submission_count(self, form_id: str):
        """Test 7: Get submission count"""
        self.log("TEST 7: Getting submission count", "🧪")
        
        response = self.make_request("GET", f"/forms/{form_id}/submissions/count")
        count_data = response.json()
        
        assert "count" in count_data
        
        self.log(f"✅ Total submissions: {count_data['count']}", "✅")
        return count_data["count"]
    
    def test_8_reorder_fields(self, form_id: str):
        """Test 8: Reorder fields"""
        self.log("TEST 8: Reordering fields", "🧪")
        
        # Get current fields
        response = self.make_request("GET", f"/forms/{form_id}/fields")
        fields = response.json()
        
        if len(fields) < 2:
            self.log("⚠️ Not enough fields to reorder", "⚠️")
            return
        
        # Create new positions (reverse order)
        reorder_data = {}
        for i, field in enumerate(reversed(fields)):
            reorder_data[field["id"]] = i
        
        self.make_request("PUT", f"/forms/{form_id}/fields/reorder", reorder_data)
        
        self.log(f"✅ Reordered {len(fields)} fields", "✅")
    
    def test_9_update_submission(self, submission_id: str):
        """Test 9: Update submission data"""
        self.log("TEST 9: Updating submission", "🧪")
        
        update_data = {
            "data": {
                "Donor Name": "Ahmed Khan (Updated)",
                "Amount (Rs)": 175,
                "Recipient": "School Fund"
            }
        }
        
        response = self.make_request("PUT", f"/forms/submissions/{submission_id}", update_data)
        updated = response.json()
        
        assert updated["data"]["Amount (Rs)"] == 175
        
        self.log("✅ Submission updated successfully", "✅")
        return updated
    
    def cleanup(self):
        """Clean up created resources"""
        self.log("CLEANUP: Removing test data", "🧹")
        
        # Delete submissions
        for submission_id in self.created_resources["submissions"]:
            try:
                self.make_request("DELETE", f"/forms/submissions/{submission_id}")
                self.log(f"Deleted submission: {submission_id}", "🗑️")
            except:
                pass
        
        # Delete forms
        for form_id in self.created_resources["forms"]:
            try:
                self.make_request("DELETE", f"/forms/{form_id}")
                self.log(f"Deleted form: {form_id}", "🗑️")
            except:
                pass
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("🚀 STARTING FORMS API INTEGRATION TESTS")
        print("="*60)
        
        try:
            # Test 1: Create form
            form = self.test_1_create_form()
            form_id = form["id"]
            time.sleep(0.5)
            
            # Test 2: Submit form
            submission = self.test_2_submit_form(form_id)
            submission_id = submission["id"]
            time.sleep(0.5)
            
            # Test 3: Add field
            self.test_3_add_field(form_id)
            time.sleep(0.5)
            
            # Test 4: Delete "Distribution Method" field
            self.test_4_delete_field(form_id, "Distribution Method")
            time.sleep(0.5)
            
            # Test 5: CRITICAL - Verify snapshot preservation
            self.test_5_verify_snapshot_preservation(submission_id, "Distribution Method")
            time.sleep(0.5)
            
            # Test 6: List submissions
            self.test_6_list_submissions(form_id)
            time.sleep(0.5)
            
            # Test 7: Get count
            self.test_7_submission_count(form_id)
            time.sleep(0.5)
            
            # Test 8: Reorder fields
            self.test_8_reorder_fields(form_id)
            time.sleep(0.5)
            
            # Test 9: Update submission
            self.test_9_update_submission(submission_id)
            
            print("\n" + "="*60)
            print("🎉 ALL TESTS PASSED!")
            print("="*60)
            
        except Exception as e:
            print("\n" + "="*60)
            print(f"❌ TEST FAILED: {e}")
            print("="*60)
            raise
        
        finally:
            # Cleanup
            cleanup_choice = input("\n🧹 Clean up test data? (y/n): ").lower()
            if cleanup_choice == 'y':
                self.cleanup()
            else:
                print("⚠️ Test data left in database for inspection")
                print(f"Form IDs: {self.created_resources['forms']}")
                print(f"Submission IDs: {self.created_resources['submissions']}")


if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         FORMS API INTEGRATION TEST SUITE                   ║
    ║         Tests against REAL database                        ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print(f"📍 API Base URL: {API_BASE_URL}")
    print(f"🔐 Auth Token: {'Set' if AUTH_TOKEN else 'Not Set (will test without auth)'}")
    
    proceed = input("\n⚠️  This will create and delete data in your REAL database. Continue? (y/n): ").lower()
    
    if proceed == 'y':
        tester = FormsAPITester(API_BASE_URL, AUTH_TOKEN)
        tester.run_all_tests()
    else:
        print("❌ Test cancelled")
