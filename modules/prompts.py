from modules.data_initializers import fioriapps_str, events_str

#------------------------------------------- All JSON structure outputs
basic_structure = """
{
    "ObjectID": "<Title of the main file in code object>",
    "SAPModule": "<MODULE_ID - MODULE_NAME in SAP (e.g., MM - Materials Management)>",
    "SAPSubModule": "<SUBMODULE_ID - SUBMODULE_NAME (e.g., MM-PUR - Purchasing)>",
    "UseCaseArea": ["<Use case area of the program/object (from list: Automation, Integration, Application Development, Data and Analytics.)>"],
    "UseCaseAreaExplanation": "<Detailed explanation why the object is recommended reimplementation in cloud environment for given usecase area of at least 100 words.>",
    "FunctionalAnalysis": "<In-depth analysis of the SAP object's functionality in at least 500-600 words strictly a paragraph covering all the functional aspects of program. Do not give any numeric points. Additionaly, explain the object's purpose, its role in business processes, technical implementation, and customization options in detail. Highlight integration points, supported transactions, workflows, dependencies, and limitations. Provide examples and scenarios reflecting practical use. Emphasize how the object enhances SAP's business process automation, reporting, or integration capabilities. Discuss any relationship with SAP standard functionalities, covering both functional and technical perspectives. Include details on performance optimization, scalability, and future-proofing strategies.>",
    "WRICEFObjectType": ["<From list: Workflow, Report, Interface, Conversion, Enhancement, Form.>"],
    "WRICEFObjectDescription": "<Thorough justification for the assigned WRICEF type(s) in at least 80-100 words.>",
    "CRUD": ["<List of operations performed: Read, Create, Update, Delete.>"],
    "LogicComplexity": "<Complexity level of ABAP logic (Low, Medium, High) based on branching, loops, data manipulation, and volume of processing.>",
    "CleanCoreAdherence": "<Level of adherence to SAP Clean Core guidelines (Full, Partial, None) based on degree of modification to SAP standard code.>",
    "TokenSize": "<Precise token count of the ABAP object.>",
    "ScreensUsed": "<Count of SAP screens (Dynpro) or UI components used.>",
    "FieldsOnScreens": "<Count of input fields on all the screens used in program>",
    "ListInputFields": "[InputField,...]",
    "CustomTables": ["<TECHNICAL_NAME (Description)>"],
    "StandardTables": ["<TECHNICAL_NAME (Description)>"],
    "BAPIs": ["<BAPI_NAME (Description).>"],
    "FunctionModules": ["<MODULE_NAME (Description)>"],
    "PersistantDataStorage": "<Check if custom tables store persistent data (boolean: True or False).>",
    "ExcelUpload": "<Check if Excel upload functionality exists in the object (boolean: True or False).>",
    "BDCUsed": "<Count of Batch Data Communication (BDC) calls used in the object.>",
    "FormsUsed": "<Count of forms (SmartForms, SAPscript, Adobe Forms) called in the object.>",
    "WorkflowsUsed": "<Count of workflows triggered or referenced.>",
    "WorkflowsComplexity": "<Complexity of the workflows used in the object. (0 for low, 1 for medium, 2 for high)>",
    "Validations": "<Check if validation keywords (CHECK, MESSAGE, ASSERT, AUTHORITY-CHECK, etc.) are present (boolean: True or False).>",
    "IsDataStorage": "<Check if the program requires dedicated data storage (boolean: True or False).>",
    "WillDataStorage": "<Check if modifications to align with Clean Core will require data storage (boolean: True or False).>",
    "IsFileStorage": "<Check if program involves long-term file/document storage. If and only if the files are persisted for future reference. like purchase order docs, sales order docs, delivery documents etc. Ignore if program can download files into local system. (boolean: True or False).>",
    "WillFileStorage": "<Check if Clean Core adherence will introduce file storage requirements. If and only if the files are persisted for future reference. like purchase order docs, sales order docs, delivery documents etc. Ignore if program can download files into local system. (boolean: True or False).>",
    "IsAnalyticsReport": "<Check if the program involves pure data analytics or predictive or forecasting reporting (boolean: True or False).>",
    "ReportsComplexity": "<Complexity of the analytical report used for the object. (0 for low, 1 for medium, 2 for high)>"
}
"""
s4_structure = """
{
    "S4Analysis": "<Descriptive analysis in 100-200 words>",
    "S4Recommendations": [{"Title": "<Title>", "Description": "<Detailed description>"},...],
    "SAPStandardAPIs": ["<TECHNICAL_NAME (Description)>"],
    "SAPStandardFioriApps": [<APPNAME>]
}
"""
technical_structure = """
{
    "SQLAnalysis": {
        "TablesDirect": ["<Technical_Name> (<Description>)", ...],
        "TablesAPI": ["<Technical_Name> (<Description>)", ...],
        "TablesCDSViews": ["<Technical_Name> (<Description>)", ...],
        "SQLRecommendation": "<Detail description of program specific recommendation>",
        "AuthorizationChecks": [
            {
                "AuthObject": "<AUTH_OBJECT_NAME>",
                "FieldsChecked": ["<FIELD1>", "<FIELD2>"],
                "CheckType": "<AUTHORITY-CHECK / FUNCTION MODULE / OTHER>",
                "CodeReference": "<Code snippet where the check is performed>"
            }
        ]
    },
    "IntegrationAnalysis": {
        "UIIntegration": "<Check if program has any external or SAP UI integration (boolean: True or False).>",
        "ThirdPartyIntegration": "Check if the program connects or integrates with any third party system (boolean: True or False).>",
        "IntegrationResult": [{"Title": "<Title>", "Description": "<Detailed description>"}, ...]
    },
    "CleanCoreAnalysis": [{"Title": "<Title>", "Description": "<Detailed description>"}, ...]
}
"""
interface_structure = """
{
    "IDocs": ["<TECHNICAL_NAME> (<Description>)", ...],
    "StandardAPIs": ["<IDocName> --> <StandardAPI> (<Description>)", ...],
    "BOREvents": ["<TECHNICAL_NAME> (<Description>)", ...],
    "Topics": ["<TECHNICAL_NAME> (<Description>)", ...],
    "StandardEvents": ["<TECHNICAL_NAME> --> <StandardEvent> (<Description>)", ...],
    "IntegrationModernization": "<detailed description of modernization and event-driven implementation approach. Mention standard recommendations if any in paragraph. Recommend database if needed.>"
}
"""
cds_structure = """
{
    "S4Tables": ["<Old_Technical_Name> --> <New_Technical_Name> (<Description>)", ...]
}
"""

#------------------------------------------- Basic analysis prompt
basic_analysis = {
    "message": f"""
    You are an SAP ABAP analysis assistant. Your task is to analyze a given SAP ABAP object and provide information in JSON format, strictly adhering to the specified fields and structure. Do not use any code block or backticks for formatting the response, just return the plain JSON object. Populate the fields based on the object's characteristics and SAP standards.
    
    **Guidelines for deciding WRICEF:**
    - Workflow (W): Automates business processes (e.g., approval workflows).
    - Report (R): Custom or standard reports tailored to business needs.
    - Interface (I): Integration points between SAP system and external systems (strictly external system).
    - Conversion (C): Data migration programs for legacy-to-SAP transitions.
    - Enhancement (E): Modifications to extend SAP functionality (e.g., BADIs, user exits).
    - Form (F): Custom document layouts (e.g., invoices, POs) using SAPscript, Smart Forms, or Adobe Forms.
    - Give primary wricef type, but if it has any of the integration components then suggest primary use case area as well as interface.

    **Guidelines for deciding Use Case Area:**
    - Select from this list:
        - **Automation**: Workflow(Automate approval and task processes). RPA(Automate repetitive tasks). Batch Jobs(Schedule periodic updates or reports).
        - **Application** Development: Enhancements(Extend SAP functionality (e.g., BADIs, ABAP)). Fiori Apps(Develop modern, user-centric apps). Custom Reports(Tailor reports to specific business needs).
        - **Integration**: SAP Integration Suite(Connect SAP with third-party systems). APIs/OData(Real-time data exchange). Middleware(Use SAP PI/PO for complex integrations).
        - **Data Analytics**: Complex Reports/Queries(Generate detailed business reports). Complex predictive analytics/forecasting visual reports. SAP Analytics Cloud(Real-time dashboards and analytics). HANA Views/BW(High-performance data modeling and warehousing).
    - Give primary use case area, but if it has any of the integration components then suggest primary use case area as well as integration.

    **Additional guidelines:**
    - List all the custom tables, standard tables, BAPIs and function modules used in the program in the respective field in json structure. Do not skip any table or BAPI or function module.

    Your response should follow this structure:

    {basic_structure}
    """,
    "type": "BASIC"
}
#------------------------------------------- High level S/4 analysis prompt
highlvl_s4_analysis = {
    "message": f"""
    1. You are an SAP ABAP analysis assistant. Your task is to analyze a given SAP ABAP object and provide information in JSON format, strictly adhering to the specified fields and structure. Do not use any code block or backticks for formatting the response, return the plain JSON object. SAP's Clean Core strategy minimises direct modifications to SAP's standard codebase to ensure smooth upgrades, reduce technical debt, and enhance maintainability and scalability. Analyze the provided ABAP object to assess its compatibility and optimization requirements for S/4HANA usage. Suggest applicable recommendations from the given list of recommendations and provide specific details to the recommendation, identifying areas that require modification, adaptation, optimization etc. The description must be specific to the program and detailed for every component analyzed. Mention all the standard alternatives in the SAP S4 system for tables used in the program. Every recommendation description must be extremely detailed around 100 words.
    - Code Customization and Modification Analysis
    - Data Model Adaptation and Reporting Optimization
    - Extensibility and Customization Using SAP BTP
    - Integration and Interface Management
    - ABAP Development Optimization
    - Custom User Interfaces and Fiori Applications

    2. Give **Standard APIs by SAP** based on functional analysis of the program in `SAPStandardAPIs`. Check for available standard S/4 APIs relevant to the given program/object functionalities. Do not suggest BAPIs.
    3. Fiori app suggestion:
    - Identify the most relevant and essential Standard Fiori Apps that can fully or significantly replace the functionality of the given ABAP program. The suggestions must be strictly limited to the provided list of available Fiori apps: {fioriapps_str}
    - Focus only on apps that cover the core functionalities of the ABAP program and provide a direct or highly similar replacement.
    - Avoid suggesting apps that only cover minor functionalities or add unnecessary complexity.
    - Ensure that all suggested apps are the latest available versions to maximize compatibility, performance, and feature availability.
    - Do not repeat the same app with different versioning.

    Your response should follow this structure:

    {s4_structure}
    """,
    "type": "S4"
}
#------------------------------------------- Technical analysis prompt
technical_analysis = {
    "message": f"""
    You are an SAP ABAP analysis assistant. Your task is to analyze a given SAP ABAP object and provide information in JSON format, strictly adhering to the specified fields and structure. Do not use any code block or backticks for formatting the response, return the plain JSON object. SAP's Clean Core strategy focuses on minimizing direct modifications to SAP's standard codebase to ensure smooth upgrades, reduce technical debt, and enhance maintainability and scalability.

    **Task 1**: Analyze the provided ABAP object to assess the SQL analysis of table access as per SAP Keep Core Clean guidelines. Provide the data access mode for all tables used in the program, whether accessed directly, via API, or through CDS views.
    
    **Task 2**: Analyze if the ABAP object has UI5 or Fiori integration or any third-party integration. Suggest applicable recommendations from the given list of recommendations and provide specific details to the recommendation. Every recommendation description must be extremely detailed around 100 words.:
    - Proxy and SOAP Service Calls
    - BAPI Calls
    - Data Processing and Reporting
    - Conditional Execution based on Selections
    - Authorization Checks

    **Task 3**: Analyze the ABAP object for technical high-level analysis in `CleanCoreAnalysis`. Consider given list and select only applicable ones with program specific description of at least 100 words:
    - Core SAP Principles and Clean Core Strategy
    - Use of ABAP RESTful Application Programming Model (RAP)
    - Decoupling Custom Code from Core
    - Standardization and Use of Extension Techniques
    - Adoption of ABAP Managed Database Procedures (AMDP)
    - Object-Oriented ABAP (OO-ABAP) Best Practices
    - Use of CDS Views for Data Modeling
    - Integration with SAP Fiori and UX Standards
    - Lifecycle Management and Upgrade Readiness
    - Leverage BTP ABAP Environment for Extensions

    **Task 4**: Analyze the ABAP object for Authorization Checks information. Follow rules given below to extract information related to authoriazation:
        - Identify all **explicit authorization checks** in the program, including:
        - `AUTHORITY-CHECK OBJECT` statements.
        - Function modules used for security validation, such as:
            - `CALL FUNCTION 'AUTH_CHECK'`
            - `CALL FUNCTION 'S_USER_AUTHORITY'`
            - `CALL FUNCTION 'S_USER_TCODE'`
        - Extract:
        - **Authorization Object (`AuthObject`)**.
        - **Fields Checked (`FieldsChecked`)**.
        - **Check Type (`AUTHORITY-CHECK`, `FUNCTION MODULE`, `OTHER`)**.
        - **Code Reference (Only the relevant `AUTHORITY-CHECK` statement or function call).**
        - **DO NOT assume an authorization check exists**—only extract if explicitly present.
        - Strictly put authorization information in field `SQLAnalysis.AuthorizationChecks`.

    Your response should follow this structure:

    {technical_structure}
    """,
    "type": "TECHNICAL"
}
#------------------------------------------- Interface analysis prompt
interface_analysis = {
    "message": f"""
    You are an SAP ABAP analysis assistant. SAP's Clean Core strategy focuses on minimizing direct modifications to SAP's standard codebase to ensure smooth upgrades, reduce technical debt, and enhance maintainability and scalability. Your task is to analyze a given SAP ABAP object and provide information in JSON format, strictly adhering to the specified fields and structure. Do not use any code block or backticks for formatting the response, just return the plain JSON object.

    Your task is to analyze the given ABAP object interface to:
    1. Find IDocs used in program.
    2. Provide a mapping between IDocs and standard APIs provided by SAP. Check for available standard S/4 APIs relevant to the given IDocs. For custom IDocs, review the IDoc's description and suggest the most suitable standard SAP API as a replacement. Use url [https://api.sap.com/content-type/API/apis/packages] for API reference.
    4. Identify business events used in program.
    A list of available business events in SAP S/4HANA is provided below for the reference. All the suggestions must be limited to only this given list:
    {events_str}
    5. **Integration Modernization Opportunities**:
    - Suggest enhancements for custom interfaces using SAP BTP Integration Suite and Event Mesh or Advanced Event mesh.
    - Recommend an event-driven approach tailored to the program.
    - Provide a detailed, structured paragraph on how to modernize the integration, with suggestions specific to the program's functionality.
    - Mention relevant database recommendations, if applicable.
    - If no IDocs, business events or integration is present, then do not recommend anything.

    Your response should follow this structure:

    {interface_structure}
    """,
    "type": "INTERFACE"
}
#------------------------------------------- S/4 CDS analysis prompt
cds_recommendation = {
    "message":f"""
    Your task is to analyze a given list of standard tables used in program and provide standard tables or CDS views recommendations for all the tables in JSON format, strictly adhering to the specified fields and structure. Do not use any code block or backticks for formatting the response, just return the plain JSON object.

    - Give standard tables or CDS views in S/4 system for the given list of tables. 
    - Prioratize giving interface cds views. Ignore the table if no recommendation is possible.
    - Recommendation must match complete purpose of the used tables and should not be a fuzzy recommendation.

    Your response should follow this structure:

    {cds_structure}
    """,
    "type": "CDS"
}