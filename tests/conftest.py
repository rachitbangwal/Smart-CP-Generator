"""
Test configuration for Smart Charter Party Generator
"""

import os
import sys
import pytest
from pathlib import Path

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_cp_generator.db"

@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory fixture"""
    return TEST_DATA_DIR

@pytest.fixture(scope="session")
def sample_recap_text():
    """Sample recap text for testing"""
    return """
    RECAP - M/V OCEAN STAR
    
    Vessel: OCEAN STAR
    Charterer: ABC Trading Ltd
    Owner: XYZ Shipping Company
    
    Cargo: 50,000 MT Iron Ore
    Loading Port: Port Hedland, Australia
    Discharge Port: Qingdao, China
    
    Freight: USD 25.50 per MT
    Laycan: 15/03/2024 - 20/03/2024
    Demurrage: USD 15,000 per day
    Despatch: USD 7,500 per day
    
    Terms: As per GENCON with usual exceptions
    """

@pytest.fixture(scope="session")
def sample_template_text():
    """Sample template text for testing"""
    return """
    CHARTER PARTY
    
    Vessel: [VESSEL_NAME]
    Charterer: [CHARTERER]
    Owner: [OWNER]
    
    Cargo: [CARGO_DESCRIPTION]
    Quantity: [CARGO_QUANTITY] MT
    
    Loading Port: [LOADING_PORT]
    Discharge Port: [DISCHARGE_PORT]
    
    Freight Rate: [FREIGHT_RATE] per MT
    Laycan: [LAYCAN_START] to [LAYCAN_END]
    """
