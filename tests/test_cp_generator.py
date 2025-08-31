"""
Tests for CPGenerator
"""

import pytest
from unittest.mock import Mock, patch
import tempfile
import os

from src.generators.cp_generator import CPGenerator


class TestCPGenerator:
    """Test cases for CPGenerator"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.generator = CPGenerator()
    
    def test_generator_initialization(self):
        """Test generator initialization"""
        assert self.generator is not None
        assert hasattr(self.generator, 'term_mappings')
        assert hasattr(self.generator, 'similarity_threshold')
        assert hasattr(self.generator, 'confidence_threshold')
    
    def test_extract_recap_terms(self):
        """Test extraction of terms from recap data"""
        recap_data = {
            "terms": {
                "freight": [
                    {
                        "value": "25.50",
                        "confidence": 0.8,
                        "full_match": "Freight: USD 25.50 per MT"
                    }
                ],
                "vessel": [
                    {
                        "value": "OCEAN STAR",
                        "confidence": 0.9,
                        "full_match": "Vessel: OCEAN STAR"
                    }
                ]
            },
            "nlp_analysis": {
                "entities": [
                    {
                        "text": "ABC Trading Ltd",
                        "label": "ORG",
                        "confidence": 0.7
                    }
                ]
            }
        }
        
        terms = self.generator._extract_recap_terms(recap_data)
        
        assert 'freight' in terms
        assert terms['freight']['value'] == "25.50"
        assert terms['freight']['confidence'] == 0.8
        
        assert 'vessel' in terms
        assert terms['vessel']['value'] == "OCEAN STAR"
        assert terms['vessel']['confidence'] == 0.9
    
    def test_find_direct_mapping(self):
        """Test direct mapping of terms"""
        recap_terms = {
            "freight": {
                "value": "25.50",
                "confidence": 0.8
            },
            "cargo": {
                "value": "Iron Ore",
                "confidence": 0.9
            }
        }
        
        # Test exact match
        result = self.generator._find_direct_mapping("freight", recap_terms)
        assert result is not None
        assert result["value"] == "25.50"
        assert result["mapping_method"] == "direct"
        
        # Test mapped term
        result = self.generator._find_direct_mapping("freight_rate", recap_terms)
        assert result is not None
        assert result["value"] == "25.50"
        assert result["mapping_method"] == "mapped"
        
        # Test no match
        result = self.generator._find_direct_mapping("unknown_field", recap_terms)
        assert result is None
    
    def test_map_entity_to_term_type(self):
        """Test mapping of NLP entities to term types"""
        assert self.generator._map_entity_to_term_type("ORG") == "charterer"
        assert self.generator._map_entity_to_term_type("GPE") == "load_port"
        assert self.generator._map_entity_to_term_type("MONEY") == "freight_rate"
        assert self.generator._map_entity_to_term_type("DATE") == "laycan_start"
        assert self.generator._map_entity_to_term_type("PRODUCT") == "cargo"
        assert self.generator._map_entity_to_term_type("UNKNOWN") is None
    
    @pytest.mark.asyncio
    async def test_map_terms_to_fields(self):
        """Test mapping of recap terms to template fields"""
        recap_terms = {
            "vessel": {
                "value": "OCEAN STAR",
                "confidence": 0.9,
                "mapping_method": "direct"
            },
            "freight": {
                "value": "25.50",
                "confidence": 0.8,
                "mapping_method": "direct"
            }
        }
        
        template_data = {
            "structured_fields": [
                {
                    "id": "field_1",
                    "type": "vessel_name",
                    "position": (10, 20),
                    "context": "Vessel name: [VESSEL_NAME]"
                },
                {
                    "id": "field_2", 
                    "type": "freight_rate",
                    "position": (50, 60),
                    "context": "Freight: [FREIGHT_RATE] per MT"
                },
                {
                    "id": "field_3",
                    "type": "charterer",
                    "position": (80, 90),
                    "context": "Charterer: [CHARTERER]"
                }
            ]
        }
        
        mappings = await self.generator._map_terms_to_fields(recap_terms, template_data)
        
        assert len(mappings) == 3
        
        # Check vessel mapping
        vessel_mapping = next(m for m in mappings if m["field_type"] == "vessel_name")
        assert vessel_mapping["filled"] == True
        assert vessel_mapping["mapped_term"]["value"] == "OCEAN STAR"
        
        # Check freight mapping  
        freight_mapping = next(m for m in mappings if m["field_type"] == "freight_rate")
        assert freight_mapping["filled"] == True
        assert freight_mapping["mapped_term"]["value"] == "25.50"
        
        # Check unmapped field
        charterer_mapping = next(m for m in mappings if m["field_type"] == "charterer")
        assert charterer_mapping["filled"] == False
    
    def test_track_changes(self):
        """Test change tracking"""
        template_data = {
            "original_data": {
                "original_text": "Test template"
            }
        }
        
        field_mappings = [
            {
                "field_id": "field_1",
                "field_type": "vessel_name",
                "field_position": (10, 20),
                "field_context": "Vessel: [VESSEL_NAME]",
                "filled": True,
                "confidence": 0.9,
                "mapped_term": {
                    "value": "OCEAN STAR",
                    "mapping_method": "direct",
                    "original_match": "Vessel: OCEAN STAR"
                }
            },
            {
                "field_id": "field_2",
                "field_type": "charterer", 
                "filled": False
            }
        ]
        
        changes = self.generator._track_changes(template_data, field_mappings)
        
        assert len(changes) == 1  # Only filled fields should have changes
        
        change = changes[0]
        assert change["field_type"] == "vessel_name"
        assert change["new_value"] == "OCEAN STAR"
        assert change["confidence"] == 0.9
        assert "timestamp" in change
    
    def test_validate_generated_document(self):
        """Test document validation"""
        filled_document = {
            "content": "Test document",
            "format": "text"
        }
        
        field_mappings = [
            {
                "field_type": "vessel_name",
                "filled": True,
                "confidence": 0.9
            },
            {
                "field_type": "charterer",
                "filled": True,
                "confidence": 0.8
            },
            {
                "field_type": "cargo",
                "filled": False,
                "confidence": 0.0
            }
        ]
        
        validation = self.generator._validate_generated_document(filled_document, field_mappings)
        
        assert "is_valid" in validation
        assert "completeness_score" in validation
        assert "confidence_score" in validation
        assert "errors" in validation
        assert "warnings" in validation
        
        # Check completeness (2 out of 3 fields filled)
        assert validation["completeness_score"] == 2/3
        
        # Check confidence (average of filled fields)
        expected_confidence = (0.9 + 0.8) / 2
        assert validation["confidence_score"] == expected_confidence
    
    def test_calculate_overall_confidence(self):
        """Test overall confidence calculation"""
        field_mappings = [
            {"filled": True, "confidence": 0.9},
            {"filled": True, "confidence": 0.7},
            {"filled": False, "confidence": 0.0},
            {"filled": True, "confidence": 0.8}
        ]
        
        confidence = self.generator._calculate_overall_confidence(field_mappings)
        
        # Should average only filled fields: (0.9 + 0.7 + 0.8) / 3
        expected = (0.9 + 0.7 + 0.8) / 3
        assert abs(confidence - expected) < 0.001
    
    def test_calculate_overall_confidence_no_filled(self):
        """Test overall confidence with no filled fields"""
        field_mappings = [
            {"filled": False, "confidence": 0.0},
            {"filled": False, "confidence": 0.0}
        ]
        
        confidence = self.generator._calculate_overall_confidence(field_mappings)
        assert confidence == 0.0
    
    @pytest.mark.asyncio
    async def test_create_html_output(self):
        """Test HTML output creation"""
        filled_text = "Test charter party content"
        modifications = [
            {
                "position": (5, 12),
                "old_text": "charter",
                "new_text": "CHARTER",
                "field_type": "test_field",
                "confidence": 0.8
            }
        ]
        
        result = await self.generator._create_html_output(filled_text, modifications)
        
        assert result["format"] == "html"
        assert result["modifications"] == modifications
        assert "content" in result
        
        # Check HTML content
        html_content = result["content"]
        assert "<!DOCTYPE html>" in html_content
        assert "CHARTER PARTY" in html_content
        assert "Changes Made:" in html_content
    
    def test_highlight_modifications_in_html(self):
        """Test HTML modification highlighting"""
        text = "This is a test text"
        modifications = [
            {
                "position": (10, 14),  # "test"
                "new_text": "TEST",
                "field_type": "test_field",
                "confidence": 0.8
            }
        ]
        
        result = self.generator._highlight_modifications_in_html(text, modifications)
        
        assert 'This is a <span class="modified">TEST</span> text' == result
    
    def test_highlight_modifications_empty(self):
        """Test HTML highlighting with no modifications"""
        text = "This is a test text"
        modifications = []
        
        result = self.generator._highlight_modifications_in_html(text, modifications)
        assert result == text
