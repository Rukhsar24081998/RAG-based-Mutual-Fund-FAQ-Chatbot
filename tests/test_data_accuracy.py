"""
Data Accuracy Validation Tests

These tests verify that SCHEME_DATA in assembler.py matches the canonical
source of truth in custom_facts.txt.

Run with: pytest tests/test_data_accuracy.py -v
"""

import os
import sys
import re
import pytest

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag.assembler import SCHEME_DATA


# Parse custom_facts.txt to get expected values
def parse_custom_facts():
    """Parse custom_facts.txt and extract all scheme data."""
    custom_facts_path = "custom_facts.txt"
    
    with open(custom_facts_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    expected = {}
    
    # Split by scheme
    schemes = content.split('\n\n')
    
    for scheme_block in schemes:
        if ':' not in scheme_block:
            continue
            
        lines = scheme_block.strip().split('\n')
        if not lines:
            continue
            
        scheme_name = lines[0].rstrip(':').strip()
        
        # Skip non-scheme headers
        if scheme_name.startswith('HDFC Mutual Fund Facts'):
            continue
        if scheme_name.startswith('How to Download'):
            continue
            
        scheme_data = {}
        
        for line in lines[1:]:
            if 'Expense Ratio' in line and 'Direct Plan' in line:
                match = re.search(r'(\d+\.\d+)%', line)
                if match:
                    scheme_data['expense_ratio'] = f"{match.group(1)}%"
            
            elif 'Minimum SIP Amount' in line:
                match = re.search(r'₹([\d,]+)', line)
                if match:
                    scheme_data['minimum_sip'] = f"₹{match.group(1)}"
            
            elif 'Exit Load' in line and not line.startswith('- Exit Load'):
                # Parse exit load text
                if '1%' in line and '1 year' in line:
                    scheme_data['exit_load'] = "An exit load of 1% is applicable if units are redeemed within 1 year from the date of allotment."
                elif '0.25%' in line and '30 days' in line:
                    scheme_data['exit_load'] = "An exit load of 0.25% is applicable if units are redeemed within 30 days from the date of allotment."
                elif '1%' in line and '15 days' in line:
                    scheme_data['exit_load'] = "An exit load of 1% is applicable if units are redeemed within 15 days from the date of allotment."
            
            elif 'Benchmark Index' in line:
                match = re.search(r'Benchmark Index: (.+)$', line)
                if match:
                    scheme_data['benchmark'] = match.group(1).strip()
            
            elif 'Riskometer Classification' in line:
                match = re.search(r'Riskometer Classification: (.+)$', line)
                if match:
                    scheme_data['riskometer'] = match.group(1).strip()
            
            elif 'Fund Manager' in line:
                match = re.search(r'Fund Manager: (.+)$', line)
                if match:
                    scheme_data['fund_manager'] = match.group(1).strip()
            
            elif 'AUM' in line and 'Assets Under Management' in line:
                match = re.search(r'₹([\d,\.]+) crore', line)
                if match:
                    scheme_data['aum'] = match.group(1).replace(',', '')
        
        if scheme_name and scheme_data:
            expected[scheme_name] = scheme_data
    
    return expected


EXPECTED_DATA = parse_custom_facts()


class TestSchemeDataAccuracy:
    """Test that SCHEME_DATA matches custom_facts.txt"""
    
    def test_all_schemes_present(self):
        """Verify all schemes from custom_facts.txt are in SCHEME_DATA"""
        for scheme in EXPECTED_DATA.keys():
            assert scheme in SCHEME_DATA, f"Missing scheme: {scheme}"
    
    def test_hdfc_flexi_cap_expense_ratio(self):
        """HDFC Flexi Cap Fund - Expense Ratio"""
        expected = EXPECTED_DATA["HDFC Flexi Cap Fund"]["expense_ratio"]
        actual = SCHEME_DATA["HDFC Flexi Cap Fund"]["expense_ratio"]
        assert actual == expected, f"Expected {expected}, got {actual}"
    
    def test_hdfc_flexi_cap_aum(self):
        """HDFC Flexi Cap Fund - AUM"""
        expected = EXPECTED_DATA["HDFC Flexi Cap Fund"]["aum"]
        actual = SCHEME_DATA["HDFC Flexi Cap Fund"]["aum"]
        assert actual == expected, f"Expected ₹{expected} Cr, got ₹{actual} Cr"
    
    def test_hdfc_flexi_cap_riskometer(self):
        """HDFC Flexi Cap Fund - Riskometer"""
        expected = EXPECTED_DATA["HDFC Flexi Cap Fund"]["riskometer"]
        actual = SCHEME_DATA["HDFC Flexi Cap Fund"]["riskometer"]
        assert actual == expected, f"Expected {expected}, got {actual}"
    
    def test_hdfc_mid_cap_expense_ratio(self):
        """HDFC Mid Cap Fund - Expense Ratio"""
        expected = EXPECTED_DATA["HDFC Mid Cap Fund"]["expense_ratio"]
        actual = SCHEME_DATA["HDFC Mid Cap Fund"]["expense_ratio"]
        assert actual == expected, f"Expected {expected}, got {actual}"
    
    def test_hdfc_mid_cap_aum(self):
        """HDFC Mid Cap Fund - AUM"""
        expected = EXPECTED_DATA["HDFC Mid Cap Fund"]["aum"]
        actual = SCHEME_DATA["HDFC Mid Cap Fund"]["aum"]
        assert actual == expected, f"Expected ₹{expected} Cr, got ₹{actual} Cr"
    
    def test_hdfc_small_cap_expense_ratio(self):
        """HDFC Small Cap Fund - Expense Ratio"""
        expected = EXPECTED_DATA["HDFC Small Cap Fund"]["expense_ratio"]
        actual = SCHEME_DATA["HDFC Small Cap Fund"]["expense_ratio"]
        assert actual == expected, f"Expected {expected}, got {actual}"
    
    def test_hdfc_small_cap_aum(self):
        """HDFC Small Cap Fund - AUM"""
        expected = EXPECTED_DATA["HDFC Small Cap Fund"]["aum"]
        actual = SCHEME_DATA["HDFC Small Cap Fund"]["aum"]
        assert actual == expected, f"Expected ₹{expected} Cr, got ₹{actual} Cr"
    
    def test_hdfc_defence_minimum_sip(self):
        """HDFC Defence Fund - Minimum SIP (was ₹500, should be ₹100)"""
        expected = EXPECTED_DATA["HDFC Defence Fund"]["minimum_sip"]
        actual = SCHEME_DATA["HDFC Defence Fund"]["minimum_sip"]
        assert actual == expected, f"Expected {expected}, got {actual}"
    
    def test_hdfc_defence_expense_ratio(self):
        """HDFC Defence Fund - Expense Ratio"""
        expected = EXPECTED_DATA["HDFC Defence Fund"]["expense_ratio"]
        actual = SCHEME_DATA["HDFC Defence Fund"]["expense_ratio"]
        assert actual == expected, f"Expected {expected}, got {actual}"
    
    def test_hdfc_defence_aum(self):
        """HDFC Defence Fund - AUM"""
        expected = EXPECTED_DATA["HDFC Defence Fund"]["aum"]
        actual = SCHEME_DATA["HDFC Defence Fund"]["aum"]
        assert actual == expected, f"Expected ₹{expected} Cr, got ₹{actual} Cr"
    
    def test_hdfc_silver_etf_expense_ratio(self):
        """HDFC Silver ETF Fund of Fund - Expense Ratio"""
        expected = EXPECTED_DATA["HDFC Silver ETF Fund of Fund"]["expense_ratio"]
        actual = SCHEME_DATA["HDFC Silver ETF Fund of Fund"]["expense_ratio"]
        assert actual == expected, f"Expected {expected}, got {actual}"
    
    def test_hdfc_silver_etf_exit_load(self):
        """HDFC Silver ETF Fund of Fund - Exit Load"""
        expected = EXPECTED_DATA["HDFC Silver ETF Fund of Fund"]["exit_load"]
        actual = SCHEME_DATA["HDFC Silver ETF Fund of Fund"]["exit_load"]
        assert actual == expected, f"Expected '{expected}', got '{actual}'"
    
    def test_hdfc_silver_etf_aum(self):
        """HDFC Silver ETF Fund of Fund - AUM"""
        expected = EXPECTED_DATA["HDFC Silver ETF Fund of Fund"]["aum"]
        actual = SCHEME_DATA["HDFC Silver ETF Fund of Fund"]["aum"]
        assert actual == expected, f"Expected ₹{expected} Cr, got ₹{actual} Cr"
    
    def test_hdfc_silver_etf_riskometer(self):
        """HDFC Silver ETF Fund of Fund - Riskometer"""
        expected = EXPECTED_DATA["HDFC Silver ETF Fund of Fund"]["riskometer"]
        actual = SCHEME_DATA["HDFC Silver ETF Fund of Fund"]["riskometer"]
        assert actual == expected, f"Expected {expected}, got {actual}"


class TestAllFieldsMatch:
    """Comprehensive test: every field in every scheme must match custom_facts.txt"""
    
    @pytest.mark.parametrize("scheme", list(SCHEME_DATA.keys()))
    def test_scheme_completeness(self, scheme):
        """Each scheme should have all required fields"""
        required_fields = ['expense_ratio', 'minimum_sip', 'exit_load', 'benchmark', 
                          'riskometer', 'fund_manager', 'aum']
        
        for field in required_fields:
            assert field in SCHEME_DATA[scheme], f"{scheme} missing field: {field}"
    
    @pytest.mark.parametrize("scheme", list(EXPECTED_DATA.keys()))
    def test_all_values_match_custom_facts(self, scheme):
        """Every value in SCHEME_DATA must match custom_facts.txt"""
        if scheme not in SCHEME_DATA:
            pytest.skip(f"{scheme} not in SCHEME_DATA")
        
        expected = EXPECTED_DATA[scheme]
        actual = SCHEME_DATA[scheme]
        
        for field, expected_value in expected.items():
            actual_value = actual.get(field, "")
            assert actual_value == expected_value, \
                f"{scheme} - {field}: Expected '{expected_value}', got '{actual_value}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
