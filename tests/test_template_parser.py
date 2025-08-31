"""
Tests for TemplateParser
"""

import pytest
from pathlib import Path
import tempfile
import os

from src.parsers.template_parser import TemplateParser


class TestTemplateParser:
    """Test cases for TemplateParser"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.parser = TemplateParser()
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        assert self.parser is not None
        assert hasattr(self.parser, 'field_patterns')
        assert hasattr(self.parser, 'template_identifiers')
        assert len(self.parser.field_patterns) > 0
    
    @pytest.mark.asyncio
    async def test_parse_simple_template(self, sample_template_text):
        """Test parsing of simple template"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(sample_template_text)
            temp_file = f.name
        
        try:
            result = await self.parser.parse(temp_file)
            
            assert 'original_text' in result
            assert 'template_type' in result
            assert 'fields' in result
            assert 'structure' in result
            assert 'clauses' in result
            assert 'file_info' in result
            
            # Should detect some fields
            fields = result['fields']
            assert len(fields) > 0
            
            # Should find vessel name field
            vessel_fields = [f for f in fields if f.get('type') == 'vessel_name']
            assert len(vessel_fields) > 0
            
        finally:
            os.unlink(temp_file)
    
    def test_identify_template_type_gencon(self):
        """Test identification of GENCON template"""
        text = "UNIFORM GENERAL CHARTER as adopted by GENCON"
        template_type = self.parser._identify_template_type(text)
        assert template_type == "GENCON"
    
    def test_identify_template_type_nype(self):
        """Test identification of NYPE template"""
        text = "NEW YORK PRODUCE EXCHANGE TIME CHARTER PARTY"
        template_type = self.parser._identify_template_type(text)
        assert template_type == "NYPE"
    
    def test_identify_template_type_unknown(self):
        """Test identification of unknown template"""
        text = "Some random charter party text"
        template_type = self.parser._identify_template_type(text)
        assert template_type == "UNKNOWN"
    
    def test_extract_fields_vessel_name(self):
        """Test extraction of vessel name fields"""
        text = "Vessel name: [VESSEL NAME] or M.V. ______"
        fields = self.parser._extract_fields(text)
        
        vessel_fields = [f for f in fields if f.get('type') == 'vessel_name']
        assert len(vessel_fields) > 0
        assert any('[vessel name]' in f.get('match', '').lower() for f in vessel_fields)
    
    def test_extract_fields_charterer(self):
        """Test extraction of charterer fields"""
        text = "Charterer: [CHARTERER] Address: _____________"
        fields = self.parser._extract_fields(text)
        
        charterer_fields = [f for f in fields if f.get('type') == 'charterer']
        assert len(charterer_fields) > 0
    
    def test_extract_fields_freight(self):
        """Test extraction of freight fields"""
        text = "Freight rate: USD _____ per metric ton"
        fields = self.parser._extract_fields(text)
        
        freight_fields = [f for f in fields if f.get('type') == 'freight_rate']
        assert len(freight_fields) > 0
    
    def test_is_duplicate_field(self):
        """Test duplicate field detection"""
        existing_fields = [
            {
                'type': 'vessel_name',
                'position': (10, 20)
            }
        ]
        
        # Overlapping field
        new_field_overlap = {
            'type': 'vessel_name', 
            'position': (15, 25)
        }
        
        # Non-overlapping field
        new_field_separate = {
            'type': 'charterer',
            'position': (50, 60)
        }
        
        assert self.parser._is_duplicate_field(existing_fields, new_field_overlap) == True
        assert self.parser._is_duplicate_field(existing_fields, new_field_separate) == False
    
    def test_get_context(self):
        """Test context extraction"""
        text = "This is a test text for context extraction around a specific position"
        position = (15, 25)  # "test text"
        context = self.parser._get_context(text, position, 10)
        
        assert "test" in context.lower()
        assert len(context) <= 30  # 10 chars before + 10 chars after + matched text
    
    def test_analyze_structure(self):
        """Test document structure analysis"""
        text = """
        CHARTER PARTY AGREEMENT
        
        1. VESSEL DETAILS
        The vessel name is ______
        
        2. CARGO INFORMATION
        - Cargo type: _____
        - Quantity: _____
        
        3. COMMERCIAL TERMS
        """
        
        structure = self.parser._analyze_structure(text)
        
        assert 'total_lines' in structure
        assert 'headers' in structure
        assert 'numbered_clauses' in structure
        assert 'bullet_points' in structure
        
        # Should find headers
        assert len(structure['headers']) > 0
        
        # Should find numbered clauses
        assert len(structure['numbered_clauses']) > 0
        
        # Should find bullet points
        assert len(structure['bullet_points']) > 0
    
    def test_extract_clauses(self):
        """Test clause extraction"""
        text = """
        1. VESSEL DESCRIPTION
        The vessel shall be described as follows...
        
        2. CARGO TERMS
        The cargo specifications are...
        
        GENERAL CONDITIONS
        These general conditions apply...
        """
        
        clauses = self.parser._extract_clauses(text)
        
        assert len(clauses) > 0
        
        # Should find numbered clauses
        numbered_clauses = [c for c in clauses if c.get('type') == 'numbered']
        assert len(numbered_clauses) >= 2
        
        # Check clause content
        vessel_clause = next((c for c in numbered_clauses if 'vessel' in c.get('title', '').lower()), None)
        assert vessel_clause is not None
        assert vessel_clause['number'] == '1'
    
    def test_extract_clause_title(self):
        """Test clause title extraction"""
        # Short descriptive text
        short_text = "VESSEL DESCRIPTION"
        title = self.parser._extract_clause_title(short_text)
        assert title == "VESSEL DESCRIPTION"
        
        # Long text - should be truncated
        long_text = "This is a very long clause description that should be truncated when used as a title because it contains too much information"
        title = self.parser._extract_clause_title(long_text)
        assert len(title) <= 53  # Should be truncated with "..."
        assert "..." in title
    
    @pytest.mark.asyncio
    async def test_parse_empty_file(self):
        """Test parsing of empty file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="No text could be extracted"):
                await self.parser.parse(temp_file)
        finally:
            os.unlink(temp_file)
