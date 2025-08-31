"""
Base CP Templates for Smart Charter Party Generator
"""

# GENCON Template Structure
GENCON_TEMPLATE = """
UNIFORM GENERAL CHARTER
(As adopted by BIMCO, CMI, FONASBA and INTERCARGO and recommended by the UN/ECE)

PART I

1. Vessel's name: [VESSEL_NAME]

2. Flag: [FLAG]

3. Port or place of registry: [REGISTRY_PORT]

4. GT/NT: [GROSS_TONNAGE]/[NET_TONNAGE]

5. DWT all told on summer/winter loadline: [DWT_SUMMER]/[DWT_WINTER] metric tons

6. Present position: [PRESENT_POSITION]

7. Expected ready to load (about): [READY_TO_LOAD_DATE]

8. Owners: [OWNERS]

9. Place of business (Owners): [OWNERS_ADDRESS]

10. Charterers: [CHARTERERS]

11. Place of business (Charterers): [CHARTERERS_ADDRESS]

12. Agents (loading): [LOADING_AGENTS]

13. Agents (discharging): [DISCHARGING_AGENTS]

14. Place of loading: [LOADING_PORT]

15. Place of discharge: [DISCHARGE_PORT]

16. Cargo (also state quantity and margin in Owners' option): [CARGO_DESCRIPTION]
    Quantity: [CARGO_QUANTITY] metric tons [QUANTITY_MARGIN]

17. Freight rate: [FREIGHT_RATE] per metric ton

18. Freight payable on: [FREIGHT_PAYMENT_TERMS]

19. Lay days (as per Clause 6): [LAYDAYS]

20. Cancelling date (as per Clause 9): [CANCELLING_DATE]

21. Loading rate: [LOADING_RATE] metric tons per weather working day

22. Discharging rate: [DISCHARGING_RATE] metric tons per weather working day

23. Demurrage rate and half demurrage rate: 
    Demurrage: [DEMURRAGE_RATE] per day
    Half demurrage: [HALF_DEMURRAGE_RATE] per day

24. Despatch rate: [DESPATCH_RATE] per day

25. Notices: [NOTICE_TIME] hours/days notice

PART II

1. It is mutually agreed that this contract shall be performed subject to the conditions contained in this Charter Party which shall include Part I and Part II.

2. LOADING
The cargo shall be brought into the holds of the vessel and properly stowed, trimmed and secured by the Charterers at their risk and expense under the supervision of the Master.

3. DISCHARGING
The cargo shall be discharged from the holds by the Charterers at their risk and expense under the supervision of the Master.

[Additional clauses continue...]
"""

# NYPE Template Structure
NYPE_TEMPLATE = """
NEW YORK PRODUCE EXCHANGE TIME CHARTER PARTY

PART I

1. Vessel's name: [VESSEL_NAME]

2. Flag and year of build: [FLAG] [YEAR_BUILT]

3. Port of registry: [REGISTRY_PORT]

4. GT/NT: [GROSS_TONNAGE]/[NET_TONNAGE]

5. DWT/Cargo capacity: [DWT]/[CARGO_CAPACITY] metric tons

6. Present position: [PRESENT_POSITION]

7. Owners: [OWNERS]

8. Place of business (Owners): [OWNERS_ADDRESS]

9. Charterers: [CHARTERERS]

10. Place of business (Charterers): [CHARTERERS_ADDRESS]

11. Place of delivery: [DELIVERY_PORT]

12. Time of delivery: [DELIVERY_TIME]

13. Place of redelivery: [REDELIVERY_PORT]

14. Time Charter period: [CHARTER_PERIOD]

15. Rate of hire: [HIRE_RATE] per day

16. Payment of hire: [HIRE_PAYMENT_TERMS]

17. Trading limits: [TRADING_LIMITS]

18. Bunkers on delivery: [BUNKERS_ON_DELIVERY] metric tons

19. Bunkers on redelivery: [BUNKERS_ON_REDELIVERY] metric tons

PART II

1. DELIVERY
The Owners shall deliver the vessel at [DELIVERY_PORT] in such dock or at such berth or place as the Charterers may direct.

2. TRADING LIMITS
The vessel shall be employed in carrying lawful merchandise only between safe ports or places where she can safely lie always afloat.

3. HIRE
The hire to be paid in advance every [HIRE_PAYMENT_FREQUENCY] days in [HIRE_CURRENCY] to the Owners.

[Additional clauses continue...]
"""

# Template mapping
TEMPLATE_MAPPING = {
    "GENCON": {
        "name": "GENCON",
        "description": "Uniform General Charter Party for dry cargo",
        "template": GENCON_TEMPLATE,
        "fields": [
            "VESSEL_NAME", "FLAG", "REGISTRY_PORT", "GROSS_TONNAGE", "NET_TONNAGE",
            "DWT_SUMMER", "DWT_WINTER", "PRESENT_POSITION", "READY_TO_LOAD_DATE",
            "OWNERS", "OWNERS_ADDRESS", "CHARTERERS", "CHARTERERS_ADDRESS",
            "LOADING_AGENTS", "DISCHARGING_AGENTS", "LOADING_PORT", "DISCHARGE_PORT",
            "CARGO_DESCRIPTION", "CARGO_QUANTITY", "QUANTITY_MARGIN", "FREIGHT_RATE",
            "FREIGHT_PAYMENT_TERMS", "LAYDAYS", "CANCELLING_DATE", "LOADING_RATE",
            "DISCHARGING_RATE", "DEMURRAGE_RATE", "HALF_DEMURRAGE_RATE", "DESPATCH_RATE",
            "NOTICE_TIME"
        ]
    },
    "NYPE": {
        "name": "NYPE",
        "description": "New York Produce Exchange Time Charter Party",
        "template": NYPE_TEMPLATE,
        "fields": [
            "VESSEL_NAME", "FLAG", "YEAR_BUILT", "REGISTRY_PORT", "GROSS_TONNAGE",
            "NET_TONNAGE", "DWT", "CARGO_CAPACITY", "PRESENT_POSITION", "OWNERS",
            "OWNERS_ADDRESS", "CHARTERERS", "CHARTERERS_ADDRESS", "DELIVERY_PORT",
            "DELIVERY_TIME", "REDELIVERY_PORT", "CHARTER_PERIOD", "HIRE_RATE",
            "HIRE_PAYMENT_TERMS", "TRADING_LIMITS", "BUNKERS_ON_DELIVERY",
            "BUNKERS_ON_REDELIVERY", "HIRE_PAYMENT_FREQUENCY", "HIRE_CURRENCY"
        ]
    }
}

def get_template(template_type: str) -> dict:
    """Get template by type"""
    return TEMPLATE_MAPPING.get(template_type.upper(), TEMPLATE_MAPPING["GENCON"])

def get_template_fields(template_type: str) -> list:
    """Get template fields by type"""
    template = get_template(template_type)
    return template.get("fields", [])

def get_available_templates() -> list:
    """Get list of available templates"""
    return list(TEMPLATE_MAPPING.keys())
