#!/usr/bin/env python3
"""
AI Forgery Document Review - PoC Detector
Author: Antigravity AI Coding Assistant
Description: Performs forensic document review and forgery detection using Gemini multimodal API.
"""

import os
import json
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from PIL import Image

# =====================================================================
# 1. Define Structured Output Schema (Pydantic Models)
# =====================================================================

class OpsRequirement(BaseModel):
    requirement_name: str = Field(
        description="Name of the operational requirement (e.g. date_visible, total_matching, vendor_identified, url_valid)"
    )
    fulfilled: bool = Field(
        description="Whether this specific operational requirement is fulfilled based on the document"
    )
    details: str = Field(
        description="Verification details or the failure reasoning if not fulfilled"
    )

class ForgeryDetectionResult(BaseModel):
    vendor_name: str = Field(
        description="Extracted name of the vendor or store (e.g., 무신사, 아디다스, 현대백화점)"
    )
    is_forged: bool = Field(
        description="Whether the document is faked or forged (True/False)"
    )
    forgery_confidence_score: float = Field(
        description="Probability score between 0.0 and 1.0 indicating how likely the document is forged"
    )
    forgery_reasoning: List[str] = Field(
        description="Detailed bullet-point reasoning for why the document is flagged as forged or faked, highlighting specific anomalies found"
    )
    ai_generation_probability: float = Field(
        description="Probability score between 0.0 and 1.0 indicating how likely this document was synthetically produced by AI"
    )
    ai_generation_reasoning: List[str] = Field(
        description="Reasoning points regarding why this document is or is not suspected of being AI-generated"
    )
    ops_requirements: List[OpsRequirement] = Field(
        description="Checklist of standard operational requirements checked on this document"
    )
    extracted_metadata: Dict[str, Any] = Field(
        description="Extracted key-value details from the document (e.g., date, order_number, total_amount, business_registration_number, store_address, url)"
    )

# =====================================================================
# 2. Programmatic Helper Validators
# =====================================================================

def validate_korean_brn(brn_str: str) -> Optional[bool]:
    """
    Validates a Korean Business Registration Number (사업자등록번호)
    Format: XXX-XX-XXXXX (10 digits)
    Returns True if valid, False if invalid, and None if no valid 10-digit number is passed.
    """
    if not brn_str:
        return None
        
    # Remove hyphens and whitespace
    digits = [int(c) for c in brn_str if c.isdigit()]
    if len(digits) != 10:
        return None
        
    # Validation algorithm
    key = [1, 3, 7, 1, 3, 7, 1, 3, 5]
    chk_sum = sum(d * k for d, k in zip(digits[:9], key))
    chk_sum += (digits[8] * 5) // 10
    remainder = chk_sum % 10
    chk_digit = (10 - remainder) % 10
    
    return digits[9] == chk_digit

def check_math_consistency(items: List[Dict[str, Any]], total: float) -> Optional[bool]:
    """
    Verifies if the sum of line items matches the stated total.
    """
    if not items:
        return None
    calculated_sum = sum(float(item.get("amount", 0)) for item in items)
    return abs(calculated_sum - total) < 1e-2

# =====================================================================
# 3. Main Forensic Detector Class
# =====================================================================

class ForgeryDetector:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the Gemini Client. 
        Looks for api_key argument first, then GEMINI_API_KEY environment variable.
        """
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError(
                "Gemini API Key is missing. Please set the GEMINI_API_KEY environment variable "
                "or pass it explicitly to ForgeryDetector(api_key='...')."
            )
        self.client = genai.Client(api_key=key)

    def analyze_document(
        self, 
        image_path: str, 
        model_name: str = "gemini-2.5-flash"
    ) -> ForgeryDetectionResult:
        """
        Performs forensic analysis on a document image.
        Uses structured outputs to enforce the ForgeryDetectionResult schema.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        print(f"[🔍] Opening image: {image_path}")
        image = Image.open(image_path)

        # Forensic prompt focusing on extracting details and evaluating credibility
        forensic_prompt = """
        You are an expert Forensic Document Examiner and Fraud Prevention Analyst. 
        Your task is to analyze the provided receipt or invoice screenshot to identify if it is faked, forged, or altered, and extract key details in a structured JSON format.

        Perform a highly meticulous review of both visual and logical components:
        1. **Textual and Logical Inconsistencies:**
           - Check dates (e.g., does the date match the order numbers or URLs?).
           - Look for spelling mistakes or brand typos in Korean (e.g., '롱삼' instead of '롱샴' for Longchamp).
           - Cross-reference store branches with their addresses. If an Adidas branch is named after a city (like Ansan '안산'), but its address is in another city (like Hanam '하남'), flag it!
           - Look for domain typosquatting in URL bars (e.g., 'muslnsa.com' with lowercase L instead of 'musinsa.com' with an i).
        2. **Visual Tampering Indicators:**
           - Font discrepancies: uneven fonts, mismatched sizes, or irregular character spacings.
           - Text alignment issues, weird block spacing, or jagged borders.
           - Signs of inspect-element modification or photo-editing overlays.
        3. **AI Generation Signs:**
           - Synthetic structural templates, unnatural spacing, blurred or missing noise, or typical hallucinated text patterns.

        Return your findings STRICTLY adhering to the schema, providing deep forensic explanations for any flagged anomalies.
        """

        print(f"[🤖] Invoking Gemini model '{model_name}' for multimodal analysis...")
        
        # Call the Gemini API with the schema
        response = self.client.models.generate_content(
            model=model_name,
            contents=[image, forensic_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ForgeryDetectionResult,
                temperature=0.1  # Low temperature for highly precise analysis
            )
        )

        # Get the parsed result
        result: ForgeryDetectionResult = response.parsed
        
        # Apply programmatic validators as an extra layer
        self._apply_programmatic_checks(result)

        return result

    def _apply_programmatic_checks(self, result: ForgeryDetectionResult):
        """
        Enhances the AI analysis with exact rule-based programmatic checks.
        """
        metadata = result.extracted_metadata
        
        # 1. Business Registration Number Validation
        brn = metadata.get("business_registration_number")
        if brn:
            is_valid_brn = validate_korean_brn(str(brn))
            if is_valid_brn is False:
                msg = f"Programmatic Check: The Business Registration Number '{brn}' failed check-digit validation."
                if msg not in result.forgery_reasoning:
                    result.is_forged = True
                    result.forgery_confidence_score = max(result.forgery_confidence_score, 0.95)
                    result.forgery_reasoning.append(msg)
                    
        # 2. Math Consistency Checks
        items = metadata.get("line_items", [])
        total = metadata.get("total_amount")
        if items and total:
            try:
                # Try to parse total
                total_val = float(re.sub(r'[^\d.]', '', str(total)))
                # Try to parse item amounts
                parsed_items = []
                for item in items:
                    amount = item.get("amount")
                    if amount:
                        amount_val = float(re.sub(r'[^\d.]', '', str(amount)))
                        parsed_items.append({"amount": amount_val})
                        
                math_ok = check_math_consistency(parsed_items, total_val)
                if math_ok is False:
                    msg = "Programmatic Check: Stated total amount does not match the sum of individual line item amounts."
                    if msg not in result.forgery_reasoning:
                        result.is_forged = True
                        result.forgery_confidence_score = max(result.forgery_confidence_score, 0.90)
                        result.forgery_reasoning.append(msg)
            except Exception:
                pass # Ignore parsing errors for math checking, defer to AI

# =====================================================================
# 4. Command-Line Entry Point
# =====================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python forgery_detector.py <path_to_document_image> [model_name]")
        sys.exit(1)
        
    img_path = sys.argv[1]
    model = sys.argv[2] if len(sys.argv) > 2 else "gemini-2.5-flash"
    
    try:
        detector = ForgeryDetector()
        report = detector.analyze_document(img_path, model_name=model)
        
        # Print a beautiful CLI Report
        print("\n" + "="*60)
        print("                 DOCUMENT FORENSIC ANALYSIS REPORT")
        print("="*60)
        print(f"File Analyzed: {img_path}")
        print(f"Vendor Detected: {report.vendor_name}")
        print("-"*60)
        
        status_text = "❌ FORGED / FAKE DETECTED" if report.is_forged else "✅ GENUINE / NO FORGERY DETECTED"
        print(f"Verdict: {status_text}")
        print(f"Forgery Confidence: {report.forgery_confidence_score * 100:.1f}%")
        print(f"AI Generation Prob: {report.ai_generation_probability * 100:.1f}%")
        print("-"*60)
        
        print("Ops Requirements Checked:")
        for req in report.ops_requirements:
            mark = "✅" if req.fulfilled else "❌"
            print(f"  {mark} {req.requirement_name}: {req.details}")
        print("-"*60)
        
        if report.forgery_reasoning:
            print("Detected Forgery Evidence & Reasoning:")
            for reason in report.forgery_reasoning:
                print(f"  • {reason}")
            print("-"*60)
            
        print("Extracted Metadata:")
        print(json.dumps(report.extracted_metadata, indent=4, ensure_ascii=False))
        print("="*60 + "\n")
        
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"Analysis Failed: {e}")
        import traceback
        traceback.print_exc()
