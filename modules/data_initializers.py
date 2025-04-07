import pandas as pd
from modules.conn import connectHANAdb, schema
import logging
from io import StringIO

logging.basicConfig(level=logging.WARNING, filename='Run.log', format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

"""
#------------------------------------------- Reference data import (local files)
# Price list
with open('./referencedata/pricelist.csv', 'r', encoding='latin1') as f_pricelist:
    pricelist_file = f_pricelist.read().replace('\xa0', ' ')

pricelist = pd.read_csv(StringIO(pricelist_file), encoding='utf-8')
pricelist.columns = pricelist.columns.str.strip().str.upper().str.replace(' ', '_')
pricelist = pricelist.replace('\xa0', ' ', regex=True).replace("Infinite", 1000000000)
pricelist["PRICE_PER_UNIT"] = pd.to_numeric(pricelist["PRICE_PER_UNIT"].str.replace(",", "", regex=True),errors="coerce")

# Fiori apps list
fioriapps = pd.read_csv('./referencedata/fioriapps.csv')
fioriapps.columns = fioriapps.columns.str.strip().str.upper().str.replace(' ', '_')
fioriapps_str = ','.join(fioriapps["APP_NAME"].dropna())

# Business events list
events_list = pd.read_csv('./referencedata/events.csv')
events_list.columns = events_list.columns.str.strip().str.upper().str.replace(' ', '_')
events_str = ','.join(events_list['EVENTNAME'].str.extract(r'beh/(.*)')[0].dropna())

# Configuration for on stack
config_all = pd.read_csv('./referencedata/configurations.csv')
config_all.columns = config_all.columns.str.strip().str.upper().str.replace(' ', '_')
config_numeric = config_all.replace("Low", "1").replace("Medium", "2").replace("High", "3")

# T-Shirt sizing
tshirt_config = pd.read_csv('./referencedata/tshirtsize.csv')
tshirt_config.columns = tshirt_config.columns.str.strip().str.upper().str.replace(' ', '_')

# Priority weights
priority_weights = pd.read_csv('./referencedata/priority_weights.csv')
priority_weights.columns = priority_weights.columns.str.strip().str.upper().str.replace(' ', '_')
"""

#------------------------------------------- Reference data import (hana db)
hdbengine = connectHANAdb()

# Price list
# pricelist = pd.read_sql(f"SELECT * FROM {schema}.KCC_REF_PRICELIST", hdbengine)

with open('./referencedata/pricelist.csv', 'r', encoding='latin1') as f_pricelist:
    pricelist_file = f_pricelist.read().replace('\xa0', ' ')
pricelist = pd.read_csv(StringIO(pricelist_file), encoding='utf-8')

pricelist.columns = pricelist.columns.str.strip().str.upper().str.replace(' ', '_')
pricelist = pricelist.replace('\xa0', ' ', regex=True).replace("Infinite", 1000000000)
pricelist["PRICE_PER_UNIT"] = pd.to_numeric(pricelist["PRICE_PER_UNIT"].str.replace(",", "", regex=True),errors="coerce")

# Fiori apps list
fioriapps = pd.read_sql(f"SELECT * FROM {schema}.KCC_REF_FIORIAPPS", hdbengine)
fioriapps.columns = fioriapps.columns.str.strip().str.upper().str.replace(' ', '_')
fioriapps_str = ','.join(fioriapps["APP_NAME"].dropna())

# Business events list
events_list = pd.read_sql(f"SELECT * FROM {schema}.KCC_REF_EVENTS", hdbengine)
events_list.columns = events_list.columns.str.strip().str.upper().str.replace(' ', '_')
events_str = ','.join(events_list['EVENTNAME'].str.extract(r'beh/(.+)')[0].dropna())

# Configuration for on stack
config_all = pd.read_sql(f"SELECT * FROM {schema}.KCC_CONFIG_MSTR a JOIN {schema}.KCC_CONFIG_DETAILS b ON a.ID = b.CONFIG_MSTR_ID", hdbengine)
config_all.columns = [f"{col}_mstr" if i == 0 else f"{col}_details" if col == "id" else col for i, col in enumerate(config_all.columns)]
config_all.columns = config_all.columns.str.strip().str.upper().str.replace(' ', '_')
config_numeric = config_all.replace("Low", "1").replace("Medium", "2").replace("High", "3")

# T-Shirt sizing
tshirt_config = pd.read_sql(f"SELECT * FROM {schema}.KCC_TSHIRT_CONFIG", hdbengine)
tshirt_config.columns = tshirt_config.columns.str.strip().str.upper().str.replace(' ', '_')

# Priority weights
priority_weights = pd.read_sql(f"SELECT * FROM {schema}.KCC_PRIORITY_CONFIG", hdbengine)
priority_weights.columns = priority_weights.columns.str.strip().str.upper().str.replace(' ', '_')

#------------------------------------------- SAP module priority
sap_mod_5 = ["FI - Financial Accounting", "CO - Controlling", "MM - Materials Management", "SD - Sales and Distribution", "PP - Production Planning", "GRC - Governance, Risk, and Compliance", "TRM - Treasury and Risk Management", "S/4HANA", "BTP - Business Technology Platform", "SCM - Supply Chain Management"]
sap_mod_4 = ["HCM - Human Capital Management", "WM - Warehouse Management", "PS - Project System", "EWM - Extended Warehouse Management", "TM - Transportation Management", "BI - Business Intelligence", "BPC - Business Planning and Consolidation"]
sap_mod_3 = ["PM - Plant Maintenance", "QM - Quality Management", "CRM - Customer Relationship Management", "SRM - Supplier Relationship Management", "CS - Customer Service", "PLM - Product Lifecycle Management", "RE-FX - Flexible Real Estate Management", "IS - Industry Solutions", "BW - Business Warehouse", "CX - Customer Experience"]