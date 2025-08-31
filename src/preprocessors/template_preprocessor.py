"""
Template Preprocessor for converting and structuring CP templates
"""

import re
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TemplatePreprocessor:
    """Preprocessor for structuring CP templates and preparing them for filling"""
    
    def __init__(self):
        # Template-specific configurations
        self.template_configs = {
            'GENCON': {
                'standard_clauses': [
                    'description of vessel',
                    'loading port',
                    'discharging port',
                    'cargo',
                    'freight',
                    'demurrage',
                    'laytime',
                    'notices'
                ],
                'required_fields': [
                    'vessel_name', 'charterer', 'owner', 'cargo', 
                    'quantity', 'load_port', 'discharge_port', 'freight_rate'
                ]
            },
            'NYPE': {
                'standard_clauses': [
                    'vessel description',
                    'period of charter',
                    'trading limits',
                    'hire rate',
                    'bunkers',
                    'delivery',
                    'redelivery'
                ],
                'required_fields': [
                    'vessel_name', 'charterer', 'owner', 'hire_rate',
                    'charter_period', 'trading_limits', 'delivery_port'
                ]
            },
            'SHELLTIME': {
                'standard_clauses': [
                    'vessel particulars',
                    'charter period',
                    'hire payment',
                    'bunkers',
                    'delivery and redelivery',
                    'employment and restrictions'
                ],
                'required_fields': [
                    'vessel_name', 'charterer', 'owner', 'hire_rate',
                    'charter_period', 'delivery_port', 'redelivery_port'
                ]
            }
        }
        
        # Field validation rules
        self.field_rules = {
            'vessel_name': {
                'type': 'text',
                'required': True,
                'validation': r'^[A-Z][A-Z0-9\s\-\.]{2,50}$'
            },
            'freight_rate': {
                'type': 'currency',
                'required': True,
                'validation': r'^\$?[\d,]+\.?\d*$'
            },
            'quantity': {
                'type': 'numeric',
                'required': True,
                'validation': r'^\d{1,6}(\.\d{1,2})?$',
                'unit': 'MT'
            },
            'charterer': {
                'type': 'text',
                'required': True,
                'validation': r'^[A-Z].{2,100}$'
            },
            'owner': {
                'type': 'text',
                'required': True,
                'validation': r'^[A-Z].{2,100}$'
            }
        }
    
    async def process(self, parsed_template: Dict[str, Any], template_type: str) -> Dict[str, Any]:
        """Process and structure a parsed template"""
        try:
            logger.info(f"Processing template of type: {template_type}")
            
            # Get template configuration
            config = self.template_configs.get(template_type, self.template_configs['GENCON'])
            
            # Structure the template data
            processed_data = {
                "template_type": template_type,
                "original_data": parsed_template,
                "structured_fields": self._structure_fields(parsed_template.get("fields", []), config),
                "field_mapping": self._create_field_mapping(parsed_template.get("fields", [])),
                "validation_rules": self._get_validation_rules(config),
                "template_structure": self._analyze_template_structure(parsed_template),
                "fillable_areas": self._identify_fillable_areas(parsed_template),
                "formatting_info": self._extract_formatting_info(parsed_template)
            }
            
            # Validate template completeness
            validation_result = self._validate_template_completeness(processed_data, config)
            processed_data["validation"] = validation_result
            
            logger.info(f"Template processing completed: {len(processed_data['structured_fields'])} fields structured")
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing template: {str(e)}")
            raise
    
    def _structure_fields(self, fields: List[Dict], config: Dict) -> List[Dict[str, Any]]:
        """Structure fields with enhanced metadata"""
        structured_fields = []
        
        for field in fields:
            structured_field = {
                "id": f"field_{len(structured_fields) + 1}",
                "type": field.get("type", "unknown"),
                "original_pattern": field.get("pattern", ""),
                "match_text": field.get("match", ""),
                "position": field.get("position", (0, 0)),
                "context": field.get("context", ""),
                "confidence": field.get("confidence", 0.5),
                "required": field.get("type", "") in config.get("required_fields", []),
                "validation_rule": self.field_rules.get(field.get("type", {})),
                "fill_priority": self._calculate_fill_priority(field, config),
                "semantic_tags": self._generate_semantic_tags(field)
            }
            
            structured_fields.append(structured_field)
        
        # Sort by fill priority
        structured_fields.sort(key=lambda x: x["fill_priority"], reverse=True)
        
        return structured_fields
    
    def _create_field_mapping(self, fields: List[Dict]) -> Dict[str, List[str]]:
        """Create mapping between field types and their positions"""
        mapping = {}
        
        for field in fields:
            field_type = field.get("type", "unknown")
            if field_type not in mapping:
                mapping[field_type] = []
            
            mapping[field_type].append({
                "position": field.get("position", (0, 0)),
                "pattern": field.get("pattern", ""),
                "context": field.get("context", "")
            })
        
        return mapping
    
    def _get_validation_rules(self, config: Dict) -> Dict[str, Any]:
        """Get validation rules for the template type"""
        rules = {}
        
        for field_type in config.get("required_fields", []):
            if field_type in self.field_rules:
                rules[field_type] = self.field_rules[field_type]
        
        return rules
    
    def _analyze_template_structure(self, parsed_template: Dict) -> Dict[str, Any]:
        """Analyze the overall structure of the template"""
        structure = parsed_template.get("structure", {})
        clauses = parsed_template.get("clauses", [])
        
        analysis = {
            "total_sections": len(structure.get("headers", [])),
            "numbered_clauses": len(structure.get("numbered_clauses", [])),
            "main_sections": [],
            "clause_hierarchy": self._build_clause_hierarchy(clauses),
            "document_flow": self._analyze_document_flow(structure, clauses)
        }
        
        # Identify main sections
        for header in structure.get("headers", []):
            analysis["main_sections"].append({
                "title": header.get("text", ""),
                "line_number": header.get("line_number", 0),
                "estimated_importance": self._estimate_section_importance(header.get("text", ""))
            })
        
        return analysis
    
    def _build_clause_hierarchy(self, clauses: List[Dict]) -> List[Dict]:
        """Build hierarchical structure of clauses"""
        hierarchy = []
        
        for clause in clauses:
            if clause.get("type") == "numbered":
                hierarchy.append({
                    "number": clause.get("number"),
                    "title": clause.get("title", ""),
                    "level": 1,  # Main clause
                    "has_subclauses": self._has_subclauses(clause.get("full_text", "")),
                    "estimated_importance": self._estimate_clause_importance(clause)
                })
        
        return hierarchy
    
    def _analyze_document_flow(self, structure: Dict, clauses: List[Dict]) -> List[str]:
        """Analyze the logical flow of the document"""
        flow = []
        
        # Standard CP flow
        expected_flow = [
            "vessel_identification",
            "parties_identification", 
            "cargo_description",
            "voyage_details",
            "commercial_terms",
            "operational_clauses",
            "legal_clauses"
        ]
        
        # Analyze actual flow based on found elements
        for clause in clauses:
            title = clause.get("title", "").lower()
            if "vessel" in title or "ship" in title:
                flow.append("vessel_identification")
            elif "charterer" in title or "owner" in title:
                flow.append("parties_identification")
            elif "cargo" in title or "commodity" in title:
                flow.append("cargo_description")
            elif "port" in title or "voyage" in title:
                flow.append("voyage_details")
            elif "freight" in title or "hire" in title:
                flow.append("commercial_terms")
        
        return list(dict.fromkeys(flow))  # Remove duplicates while preserving order
    
    def _identify_fillable_areas(self, parsed_template: Dict) -> List[Dict[str, Any]]:
        """Identify areas in the template that can be filled"""
        fillable_areas = []
        text = parsed_template.get("original_text", "")
        
        # Find blank lines or spaces that might be fillable
        blank_patterns = [
            r'_{3,}',  # Multiple underscores
            r'\.{3,}',  # Multiple dots
            r'\s{10,}',  # Large spaces
            r'\[.*?\]',  # Bracketed placeholders
            r'\(.*?\)',  # Parenthetical placeholders
        ]
        
        for i, pattern in enumerate(blank_patterns):
            matches = re.finditer(pattern, text)
            for match in matches:
                area = {
                    "id": f"area_{len(fillable_areas) + 1}",
                    "pattern_type": f"pattern_{i + 1}",
                    "position": match.span(),
                    "original_text": match.group(0),
                    "context": self._get_context(text, match.span(), 30),
                    "estimated_field_type": self._estimate_field_type_from_context(
                        self._get_context(text, match.span(), 50)
                    )
                }
                fillable_areas.append(area)
        
        return fillable_areas
    
    def _extract_formatting_info(self, parsed_template: Dict) -> Dict[str, Any]:
        """Extract formatting information to preserve document structure"""
        text = parsed_template.get("original_text", "")
        
        formatting = {
            "line_breaks": text.count('\n'),
            "paragraph_breaks": len(re.findall(r'\n\s*\n', text)),
            "indentation_patterns": self._analyze_indentation(text),
            "heading_styles": self._analyze_heading_styles(parsed_template.get("structure", {})),
            "numbering_schemes": self._analyze_numbering_schemes(text),
            "special_characters": self._count_special_characters(text)
        }
        
        return formatting
    
    def _validate_template_completeness(self, processed_data: Dict, config: Dict) -> Dict[str, Any]:
        """Validate that the template has all required components"""
        validation = {
            "is_complete": True,
            "missing_fields": [],
            "warnings": [],
            "score": 0.0
        }
        
        required_fields = config.get("required_fields", [])
        found_field_types = [field["type"] for field in processed_data.get("structured_fields", [])]
        
        # Check for missing required fields
        for required_field in required_fields:
            if required_field not in found_field_types:
                validation["missing_fields"].append(required_field)
                validation["is_complete"] = False
        
        # Calculate completeness score
        if required_fields:
            found_required = len([f for f in found_field_types if f in required_fields])
            validation["score"] = found_required / len(required_fields)
        
        # Add warnings
        if validation["score"] < 0.8:
            validation["warnings"].append("Template may be incomplete - some required fields not detected")
        
        if len(processed_data.get("structured_fields", [])) < 5:
            validation["warnings"].append("Very few fields detected - template may need manual review")
        
        return validation
    
    def _calculate_fill_priority(self, field: Dict, config: Dict) -> int:
        """Calculate priority for filling this field"""
        priority = 50  # Base priority
        
        # Higher priority for required fields
        if field.get("type", "") in config.get("required_fields", []):
            priority += 30
        
        # Higher priority for higher confidence
        priority += int(field.get("confidence", 0.5) * 20)
        
        # Higher priority for fields earlier in document
        position = field.get("position", (1000, 1000))[0]
        if position < 1000:
            priority += max(0, 20 - (position // 100))
        
        return priority
    
    def _generate_semantic_tags(self, field: Dict) -> List[str]:
        """Generate semantic tags for a field"""
        tags = []
        field_type = field.get("type", "")
        context = field.get("context", "").lower()
        
        # Add type-based tags
        if field_type:
            tags.append(f"type:{field_type}")
        
        # Add context-based tags
        if "port" in context:
            tags.append("location")
        if "date" in context or "time" in context:
            tags.append("temporal")
        if "$" in context or "usd" in context or "rate" in context:
            tags.append("financial")
        if "cargo" in context or "commodity" in context:
            tags.append("cargo_related")
        
        return tags
    
    def _estimate_section_importance(self, section_title: str) -> int:
        """Estimate the importance of a section (1-10)"""
        title_lower = section_title.lower()
        
        # Critical sections
        if any(word in title_lower for word in ['vessel', 'cargo', 'freight', 'charter']):
            return 9
        
        # Important sections
        if any(word in title_lower for word in ['port', 'delivery', 'payment', 'terms']):
            return 7
        
        # Standard sections
        if any(word in title_lower for word in ['notice', 'clause', 'condition']):
            return 5
        
        return 3
    
    def _has_subclauses(self, clause_text: str) -> bool:
        """Check if a clause has subclauses"""
        # Look for lettered or numbered sub-items
        return bool(re.search(r'\n\s*[a-z]\)', clause_text) or 
                   re.search(r'\n\s*\(\d+\)', clause_text))
    
    def _estimate_clause_importance(self, clause: Dict) -> int:
        """Estimate the importance of a clause"""
        title = clause.get("title", "").lower()
        
        # Very important clauses
        if any(word in title for word in ['vessel', 'cargo', 'freight', 'payment']):
            return 9
        
        # Important clauses
        if any(word in title for word in ['port', 'delivery', 'time', 'notice']):
            return 7
        
        # Standard clauses
        return 5
    
    def _get_context(self, text: str, position: tuple, context_length: int = 30) -> str:
        """Get context around a position"""
        start = max(0, position[0] - context_length)
        end = min(len(text), position[1] + context_length)
        return text[start:end].strip()
    
    def _estimate_field_type_from_context(self, context: str) -> str:
        """Estimate field type from surrounding context"""
        context_lower = context.lower()
        
        if "vessel" in context_lower or "ship" in context_lower:
            return "vessel_name"
        elif "cargo" in context_lower or "commodity" in context_lower:
            return "cargo"
        elif "port" in context_lower:
            if "load" in context_lower:
                return "load_port"
            elif "discharge" in context_lower:
                return "discharge_port"
            else:
                return "port"
        elif "freight" in context_lower or "$" in context_lower:
            return "freight_rate"
        elif "charterer" in context_lower:
            return "charterer"
        elif "owner" in context_lower:
            return "owner"
        
        return "unknown"
    
    def _analyze_indentation(self, text: str) -> Dict[str, int]:
        """Analyze indentation patterns in the text"""
        lines = text.split('\n')
        indentation_counts = {}
        
        for line in lines:
            if line.strip():  # Skip empty lines
                leading_spaces = len(line) - len(line.lstrip())
                indentation_counts[leading_spaces] = indentation_counts.get(leading_spaces, 0) + 1
        
        return indentation_counts
    
    def _analyze_heading_styles(self, structure: Dict) -> List[Dict]:
        """Analyze heading styles"""
        styles = []
        
        for header in structure.get("headers", []):
            styles.append({
                "text": header.get("text", ""),
                "is_uppercase": header.get("text", "").isupper(),
                "length": len(header.get("text", "")),
                "line_number": header.get("line_number", 0)
            })
        
        return styles
    
    def _analyze_numbering_schemes(self, text: str) -> List[str]:
        """Analyze numbering schemes used in the document"""
        schemes = []
        
        if re.search(r'^\s*\d+\.', text, re.MULTILINE):
            schemes.append("numeric_dot")
        if re.search(r'^\s*[a-z]\)', text, re.MULTILINE):
            schemes.append("letter_parenthesis")
        if re.search(r'^\s*\([a-z]\)', text, re.MULTILINE):
            schemes.append("parenthesis_letter")
        if re.search(r'^\s*[ivx]+\.', text, re.MULTILINE):
            schemes.append("roman_dot")
        
        return schemes
    
    def _count_special_characters(self, text: str) -> Dict[str, int]:
        """Count special characters that might be significant"""
        return {
            "underscores": text.count('_'),
            "brackets": text.count('[') + text.count(']'),
            "parentheses": text.count('(') + text.count(')'),
            "dollar_signs": text.count('$'),
            "percent_signs": text.count('%')
        }
