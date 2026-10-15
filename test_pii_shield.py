from app.pii_shield import detect_pii, mask_pii

sample_text = """
Employee Name: Rahul Sharma
Email: rahul.sharma@example.com
Phone: 9876543210

Alternate Phone: +91-9876543210
Office Contact: 09876543210

Employee ID: 1234567890
Policy Reference: ISO 27001
Audit Finding: Access review was not completed.
"""

results = detect_pii(sample_text)

for result in results:
    print(result)

print("\nMasked Document:")
print(mask_pii(sample_text))