import logging

logging.basicConfig(level=logging.WARNING, filename='Run.log', format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


#------------------------------------------- Analyze input code/data for input prompt object
from modules.conn import createOpenAIClient, deployment
ai_client = createOpenAIClient()

def analyzeBatch(prompt_data: dict, code_object: str):
    prompt_message, prompt_type = prompt_data["message"], prompt_data["type"]
    if(prompt_type=='CDS'): input_message = f"Suggest S/4 cds views/tables for these standard tables:\n{code_object}"
    elif(prompt_type in ['BASIC','S4','TECHNICAL','INTERFACE']): input_message = f"ABAP Object:\n{code_object}"
    else: input_message = code_object

    messages = [{"role": "system", "content": prompt_message}, {"role": "user", "content": input_message}]    
    try:
        completion = ai_client.chat.completions.create(
            model=deployment,
            messages=messages,
            max_tokens=4000,
            temperature=0,
            seed=42
        )

        response = completion.choices[0].message.content
        if not response: raise ValueError(f"Empty model response")
        # with open(f"./content/{prompt_type.lower()}.json", "w") as file:
        #     file.write(response)
        return response
    except Exception as e:
        if hasattr(e, 'code') and e.code == 'context_length_exceeded': logger.error(f"e0f12: {e}")
        elif hasattr(e, 'code') and e.code == 'DeploymentNotFound': logger.error(f"e0f13: {e}")
        else: logger.error(f"e0f11: {e}")
        return None
    
#------------------------------------------- Parse string input to  json object
import json

def parseResponse(response: str):
    try: return json.loads(response)
    except json.JSONDecodeError: return response
    except: return None

#------------------------------------------- Get value and typecase
def get_value(dictionary, key, cast_func=lambda x: x):
    try: 
        if cast_func == bool: return str(dictionary[key]).lower() in {"true", "1"}
        return cast_func(dictionary[key])
    except: 
        if cast_func == str: return ""
        elif cast_func == list: return []
        elif cast_func == dict: return {}
        elif cast_func == int: return 0
        return None

#------------------------------------------- Check if object is interface
def isInterface(parsed_basic_analysis: dict):
    if(not parsed_basic_analysis): return False
    if "interface" in [item.lower() for item in parsed_basic_analysis.get("WRICEFObjectType", [])]: return True
    return False
#------------------------------------------- Check if object is report
def isReport(parsed_basic_analysis: dict):
    if(not parsed_basic_analysis): return False
    if "report" in [item.lower() for item in parsed_basic_analysis.get("WRICEFObjectType", [])]: return True
    return False
#------------------------------------------- Check if use case is integration
def isIntegration(parsed_basic_analysis: dict):
    if(not parsed_basic_analysis): return False
    if "integration" in [item.lower() for item in parsed_basic_analysis.get("UseCaseArea", [])]: return True
    return False
#------------------------------------------- Check if use case is automation
def isAutomation(parsed_basic_analysis: dict):
    if(not parsed_basic_analysis): return False
    if "automation" in [item.lower() for item in parsed_basic_analysis.get("UseCaseArea", [])]: return True
    return False
#------------------------------------------- Check if use case is app dev
def isAppDev(parsed_basic_analysis: dict):
    if(not parsed_basic_analysis): return False
    if "application development" in [item.lower() for item in parsed_basic_analysis.get("UseCaseArea", [])]: return True
    return False
#------------------------------------------- Check if use case is data analytics
def isDataAnalytics(parsed_basic_analysis: dict):
    if(not parsed_basic_analysis): return False
    if "data analytics" in [item.lower() for item in parsed_basic_analysis.get("UseCaseArea", [])]: return True
    return False
#------------------------------------------- Check if use case is app dev and automation
def isAppDevAutomation(parsed_basic_analysis: dict):
    if(not parsed_basic_analysis): return False
    if(isAppDev(parsed_basic_analysis) and isAutomation(parsed_basic_analysis)): return True
    return False

#------------------------------------------- Check if object is interface
def successParsing(filename: str, analysis: dict, analysis_type: str):
    if not analysis or not isinstance(analysis, dict):
        logger.error(f"e1f11:[{filename}] {analysis_type} analysis could not be completed. Skipping further analysis.")
        return False
    # print(f"{filename}: passed {analysis_type}")
    return True

#------------------------------------------- Batch analysis of the code
from modules.prompts import basic_analysis, highlvl_s4_analysis, technical_analysis, interface_analysis

def analyzeCode(code_object: str, filename: str):
    output_basic_analysis = analyzeBatch(basic_analysis, code_object)
    parsed_basic_analysis = parseResponse(output_basic_analysis)
    if not successParsing(filename, parsed_basic_analysis, "_Basic"): return

    output_s4_analysis = analyzeBatch(highlvl_s4_analysis, code_object)
    parsed_s4_analysis = parseResponse(output_s4_analysis)
    if not successParsing(filename, parsed_s4_analysis, "_S4"): return

    output_technical_analysis = analyzeBatch(technical_analysis, code_object)
    parsed_technical_analysis = parseResponse(output_technical_analysis)
    if not successParsing(filename, parsed_technical_analysis, "_Technical"): return

    if isInterface(parsed_basic_analysis): output_interface_analysis = analyzeBatch(interface_analysis, code_object)
    else: output_interface_analysis = '{"IDocs": [],"StandardAPIs": [],"Events": [],"StandardEvents": [],"IntegrationModernization": ""}'
    parsed_interface_analysis = parseResponse(output_interface_analysis)
    if not successParsing(filename, parsed_interface_analysis, "_Interface"): return

    complete_analysis = {
        "basic_analysis": parsed_basic_analysis,
        "highlvl_s4_analysis": parsed_s4_analysis,
        "technical_analysis": parsed_technical_analysis,
        "interface_analysis": parsed_interface_analysis
    }

    missing_keys = [key for key in complete_analysis if not complete_analysis[key]]
    if missing_keys: return logger.error(f"e1f12: Analysis is missing keys: {missing_keys}")
    return complete_analysis

#------------------------------------------- Extract essential fields from analysis
def extractEssentials(complete_analysis: dict):          
    __basic_analysis = complete_analysis["basic_analysis"]
    __integration_analysis = complete_analysis["technical_analysis"]["IntegrationAnalysis"]
    __interface_analysis = complete_analysis["interface_analysis"]
    return {
        "sap_module": get_value(__basic_analysis, "SAPModule"),
        "usecase_area": get_value(__basic_analysis, "UseCaseArea", list),
        "codelength": get_value(__basic_analysis, "CodeLength", int),
        "custom_tables": get_value(__basic_analysis, "CustomTables", list),
        "standard_tables": get_value(__basic_analysis, "StandardTables", list),
        "bapis": get_value(__basic_analysis, "BAPIs", list),
        "function_modules": get_value(__basic_analysis, "FunctionModules", list),
        "events": get_value(__interface_analysis, "Events", list),
        "standard_events": get_value(__interface_analysis, "StandardEvents", list),
        "screens_count": get_value(__basic_analysis, "ScreensUsed", int),
        "ui_fields_count": get_value(__basic_analysis, "FieldsOnScreens", int),
        "reports_complexity": get_value(__basic_analysis, "ReportsComplexity", int),
        "workflows_count": get_value(__basic_analysis, "WorkflowsUsed", int),
        "workflows_complexity": get_value(__basic_analysis, "WorkflowsComplexity", int),
        "forms_count": get_value(__basic_analysis, "FormsUsed", int),
        "excel_upload": get_value(__basic_analysis, "ExcelUpload", lambda x: bool(int(x))),
        "bdcs_count": get_value(__basic_analysis, "BDCUsed", int),
        "validations": get_value(__basic_analysis, "Validations", bool),
        "crud_ops": set(map(str.lower, get_value(__basic_analysis, "CRUD", list) or [])),
        "persistant_storage": get_value(__basic_analysis, "PersistantDataStorage", bool),
        "will_data_storage": get_value(__basic_analysis, "WillDataStorage", bool),
        "is_data_storage": get_value(__basic_analysis, "IsDataStorage", bool),
        "is_file_storage": get_value(__basic_analysis, "IsFileStorage", bool),
        "will_file_storage": get_value(__basic_analysis, "WillFileStorage", bool),
        "is_analytical_report": get_value(__basic_analysis, "IsAnalyticsReport", bool),
        "ui_intgr": get_value(__integration_analysis, "UIIntegration", bool),
        "thirdparty_intgr": get_value(__integration_analysis, "ThirdPartyIntegration", bool),
    }

#------------------------------------------- Enhancement 1: Code length
def addCodeLines(code_object: str, complete_analysis: dict):
    lines = code_object.splitlines()
    code_lines = 0
    for line in lines:
        stripped_line = line.strip()                
        if stripped_line and not stripped_line.startswith("*"): code_lines += 1
    complete_analysis["basic_analysis"]["CodeLength"] = str(code_lines)
    # print(f'--- Added code lines: {str(code_lines)}')
    return complete_analysis

#------------------------------------------- Enhancement 2: Coupling & approach
def addCoupling(complete_analysis: dict):
    stats = extractEssentials(complete_analysis)
    custom_tables_count, standard_tables_count = len(stats["custom_tables"]), len(stats["standard_tables"])
    table_ratio = custom_tables_count/(standard_tables_count or 1)
    has_BDC = stats["bdcs_count"]
    has_excelupload = stats["excel_upload"]
    is_integration = any (i.lower() == "integration" for i in stats["usecase_area"])
    is_thirdpary_intgr = stats["thirdparty_intgr"]
    if(has_BDC or has_excelupload or table_ratio>0.6 or is_integration or is_thirdpary_intgr):
        coupling ="loose"
        approach = "side-by-side"
    else:
        coupling ="tight"
        approach = "on-stack"
    complete_analysis["basic_analysis"]["Coupling"] = coupling
    complete_analysis["basic_analysis"]["RecommendedApproach"] = approach
    # print(f'--- Added coupling: {complete_analysis["basic_analysis"]["Coupling"]}')
    # print(f'--- Added approach: {complete_analysis["basic_analysis"]["RecommendedApproach"]}')
    return complete_analysis

#------------------------------------------- Enhancement 3: Fiori apps Ids
from rapidfuzz import process, fuzz
from modules.data_initializers import fioriapps

def addFioriAppId(complete_analysis: dict):
    if(not complete_analysis): return complete_analysis
    fiori_apps_input = complete_analysis.get("highlvl_s4_analysis", {}).get("SAPStandardFioriApps", [])
    if(fiori_apps_input):
        fiori_apps_output = []
        for app_name in fiori_apps_input:
            app_match = fioriapps[fioriapps['APP_NAME'].str.lower() == app_name.lower()]
            if not app_match.empty: fiori_apps_output.append(f"{app_match.iloc[0]['FIORI_ID']} ({app_name})")
            else:
                match_result = process.extractOne(app_name.lower(), fioriapps['APP_NAME'].tolist(), scorer=fuzz.WRatio, score_cutoff=85)
                
                if match_result:
                    close_match, score = match_result[:2]
                    matched_id = fioriapps.loc[fioriapps['APP_NAME'] == close_match, 'FIORI_ID'].values[0]
                    fiori_apps_output.append(f"{matched_id} ({close_match})*")
                else: fiori_apps_output.append(f"{app_name}**")
        complete_analysis["highlvl_s4_analysis"]["SAPStandardFioriApps"] = fiori_apps_output
    # print(f'--- Added {len(complete_analysis["highlvl_s4_analysis"]["SAPStandardFioriApps"])} Fiori apps')
    return complete_analysis

#------------------------------------------- Enhancement 4: CDS views
from modules.prompts import cds_recommendation

def addCDSViews(filename: str, complete_analysis: dict):
    if(not complete_analysis): return complete_analysis
    tables_used = list(set(complete_analysis["basic_analysis"]["CustomTables"]+complete_analysis["basic_analysis"]["StandardTables"]))
    if(tables_used):
        new_s4_views = analyzeBatch(cds_recommendation, tables_used)
        parsed_s4_views = parseResponse(new_s4_views)
        if not successParsing(filename, parsed_s4_views, "_CDS"): 
            print(f'--x Failed to add CDS views')
            return
        complete_analysis["technical_analysis"]["SQLAnalysis"]["S4Tables"] = parsed_s4_views["S4Tables"]
    # print(f'--- Added {len(complete_analysis["technical_analysis"]["SQLAnalysis"]["S4Tables"])} CDS views')
    return complete_analysis

#------------------------------------------- Enhancement 5: Implementation efforts
from modules.effort_estimators import getEstHours, getTShirtSize

def addEfforts(complete_analysis: dict):
    if(not complete_analysis): return complete_analysis
    est_efforts = getEstHours(complete_analysis)
    tshirt_size = getTShirtSize(est_efforts)
    complete_analysis["basic_analysis"]["ManEfforts"] = str(sum(est_efforts.values()) - est_efforts["code_hours"])
    complete_analysis["basic_analysis"]["TShirtSize"] = tshirt_size
    # print(f'--- Added efforts hours: {complete_analysis["basic_analysis"]["ManEfforts"]}')
    # print(f'--- Added tshirt size: {complete_analysis["basic_analysis"]["TShirtSize"]}')
    return complete_analysis

#------------------------------------------- Enhancement 6: Implementation priority
from modules.effort_estimators import getPriority

def addPriority(complete_analysis: dict):
    if(not complete_analysis): return complete_analysis
    priority = getPriority(complete_analysis)
    complete_analysis["basic_analysis"]["Priority"] = priority
    # print(f'--- Added priority: {complete_analysis["basic_analysis"]["Priority"]}')
    return complete_analysis

#------------------------------------------- Enhancement 7: Basic BTP services
from modules.service_estimators import getBasicServices, getDevelopmentApproach, getDevelopmentServices, estimateServicePricing

def addDevelopmentApproach(complete_analysis: dict, skillset: str):
    approach = getDevelopmentApproach(complete_analysis, skillset)
    complete_analysis["technical_analysis"]["DevelopmentApproach"] = approach
    # print(f'--- Added Development approach: {complete_analysis["technical_analysis"]["DevelopmentApproach"]}')

    return complete_analysis

def addBasicServices(complete_analysis: dict, skillset: str):
    if(not complete_analysis): return complete_analysis
    basic_services = getBasicServices(complete_analysis) or []
    development_services = getDevelopmentServices(complete_analysis, skillset) or []
    all_basic_services = basic_services + development_services

    complete_analysis["technical_analysis"]["BTPServices"] = all_basic_services
    # print(f'--- Added {len(complete_analysis["technical_analysis"]["BTPServices"])} basic BTP services')

    return complete_analysis

#------------------------------------------- Enhancement 8: Basic BTP services pricing
def addBasicServicesPricing(complete_analysis: dict):
    if(not complete_analysis): return complete_analysis
    services = complete_analysis["technical_analysis"]["BTPServices"] or []
    services_pricing = estimateServicePricing(services)
    complete_analysis["technical_analysis"]["BTPServices"] = services_pricing
    # print(f'--- Added {len(complete_analysis["technical_analysis"]["BTPServices"])} basic BTP services with pricing')
    return complete_analysis

#------------------------------------------- Additional Enhancement 1: Custom BTP services and pricing
from modules.service_estimators import getCustomServices

def addCustomServicesPricing(complete_analysis: dict, qna: list):
    if(not complete_analysis): return complete_analysis
    services = getCustomServices(qna)
    services_pricing = estimateServicePricing(services)
    # print(f'--- Added {len(complete_analysis["technical_analysis"]["BTPServices"])} additional BTP services with pricing')
    return services_pricing

#------------------------------------------- Additional Enhancement 2: Custom BTP services and pricing
from modules.effort_estimators import quantifyMigrationEfforts

def addMigrationEfforts(complete_analysis: dict):
    if(not complete_analysis): return complete_analysis
    total_hours = quantifyMigrationEfforts(complete_analysis)
    coupling = complete_analysis["basic_analysis"]["Coupling"]

    if coupling.lower()=="loose": 
        complete_analysis["basic_analysis"]["ManEfforts"] = str(total_hours)
        complete_analysis["basic_analysis"]["TShirtSize"] = getTShirtSize(total_hours)
    # print(f'--- Added migration efforts hours: {complete_analysis["basic_analysis"]["ManEfforts"]}')
    # print(f'--- Updated tshirt size: {complete_analysis["basic_analysis"]["TShirtSize"]}')
    
    return complete_analysis

#------------------------------------------- Additional Enhancement 3: Clear irrelevant recommendations
def filterRecommendations(complete_analysis: dict):
    if(not complete_analysis): return complete_analysis
    s4recommendations = complete_analysis["highlvl_s4_analysis"]["S4Recommendations"]
    coupling = complete_analysis["basic_analysis"]["Coupling"]
    usecase_areas = complete_analysis["basic_analysis"]["UseCaseArea"]
    filtered_recommendations = s4recommendations
    
    if coupling.lower() == "tight":
        filtered_recommendations = [item for item in filtered_recommendations if item["Title"] != "Extensibility and Customization Using SAP BTP"]
        complete_analysis["technical_analysis"]["BTPServices"] = []
        complete_analysis["basic_analysis"]["UseCaseArea"] = []
        complete_analysis["basic_analysis"]["UseCaseAreaExplanation"] = ""
        complete_analysis["technical_analysis"]["DevelopmentApproach"] = ""
    if not any("integration" in item.lower() for item in usecase_areas):
        filtered_recommendations = [item for item in filtered_recommendations if item["Title"] != "Integration and Interface Management"]
        
    complete_analysis["highlvl_s4_analysis"]["S4Recommendations"] = filtered_recommendations

    # print(f'--- Cleared irrelevant recommendations (if any): {len(s4recommendations)} -> {len(complete_analysis["highlvl_s4_analysis"]["S4Recommendations"])}')
    return complete_analysis

#------------------------------------------- Additional Enhancement 4: Extend implementation efforts
from modules.effort_estimators import getExtendedEfforts
def addExtendedEfforts(complete_analysis: dict):
    if(not complete_analysis): return complete_analysis
    efforts_breakdown = getExtendedEfforts(complete_analysis)
    extended_hours = int(efforts_breakdown["total_hours"])
    complete_analysis["basic_analysis"]["ManEfforts"] = str(extended_hours)
    complete_analysis["basic_analysis"]["TShirtSize"] = getTShirtSize(extended_hours/2)
    # print(f'--- Updated efforts: {complete_analysis["basic_analysis"]["ManEfforts"]}')
    # print(f'--- Updated tshirt size(re): {complete_analysis["basic_analysis"]["TShirtSize"]}')
    return complete_analysis


#------------------------------------------- Enhancements applied
def enhanceAnalysis(filename: str, code_object: str, complete_analysis: dict, skillset: str):
    enhancement01 = addCodeLines(code_object, complete_analysis)
    enhancement02 = addFioriAppId(enhancement01)
    enhancement03 = addCDSViews(filename, enhancement02)
    enhancement04 = addCoupling(enhancement03)
    enhancement05 = addEfforts(enhancement04)
    enhancement06 = addPriority(enhancement05)
    enhancement07 = addDevelopmentApproach(enhancement06, skillset)
    enhancement08 = addBasicServices(enhancement07, skillset)
    enhancement09 = addBasicServicesPricing(enhancement08)
    enhancement10 = addMigrationEfforts(enhancement09)
    enhancement11 = filterRecommendations(enhancement10)
    enhancement12 = addExtendedEfforts(enhancement11)

    with open("./content/enhanced_output.json", "w") as file:
        file.write(json.dumps(enhancement12, indent=4))

    return enhancement12