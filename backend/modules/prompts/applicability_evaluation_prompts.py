'''
-Capital market oriented companies
-Number of employees
-Assets
-Revenue
-Offering of financial products
-Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)
-Manufacturers or distributors of batteries
-Jurisdiction
-Markets (countries)
-Sourcing (countries)
-Production (Countries)
-Products and Services offered
'''

search_prompt_capital_market_oriented = "determine if this regulation applies to this company based on its capital market orientation."

prompt_capital_market_oriented = '''
Given the following ESG legal document,
and considering that company {company_name} {is_capital_market_oriented} a capital market oriented company
determine if this regulation applies to this company based on its capital market orientation.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_number_of_employees = "determine if this regulation applies to this company based on its number of employees."

prompt_number_of_employees = '''
Given the following ESG legal document, and considering that company {company_name} has {num_employees} employees
determine if this regulation applies to this company based on its number of employees.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_assets = "determine if this regulation applies to this company based on its assets."

prompt_assets = '''
Given the following ESG legal document,
and considering that company {company_name} has {assets}{currency} in assets
determine if this regulation applies to this company based on its assets in {currency}.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_revenue = "determine if this regulation applies to this company based on its annual revenue."

prompt_revenue = '''
Given the following ESG legal document,
and considering that company {company_name} perceives {revenue}{currency} in annual revenue
determine if this regulation applies to this company based on its annual revenue in {currency}.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_offering_of_financial_products = "determine if this regulation applies to this company based on whether it offers financial products."

prompt_offering_of_financial_products = '''
Given the following ESG legal document,
and considering that company {company_name} {is_offering_financial_products} financial products
determine if this regulation applies to this company based on whether it offers financial products.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_scope_of_the_REACH = "determine if this regulation applies to this company based on the scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH) regulation."

prompt_scope_of_the_REACH = '''
Given the following ESG legal document,
and considering that company {company_name} {is_REACH} subject to the REACH regulation
determine if this regulation applies to this company based on the scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH) regulation.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_batteries = "determine if this regulation applies to this company based on whether it is a manufacturer or distributor of batteries."

prompt_batteries = '''
Given the following ESG legal document,
and considering that company {company_name} {is_battery} a manufacturer or distributor of batteries
determine if this regulation applies to this company based on whether it is a manufacturer or distributor of batteries.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

# prompt_date_of_applicability = '''
# Given the following ESG legal document with their regulation name, and

search_prompt_jurisdiction = "determine if this regulation applies to this company based on its jurisdiction."

prompt_jurisdiction = '''
Given the following ESG legal document,
and considering that company {company_name} is subject to the jurisdiction of {jurisdiction}
determine if this regulation applies to this company based on its jurisdiction.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_markets = "determine if this regulation applies to this company based on the markets it operates in."

prompt_markets = '''
Given the following ESG legal document,
and considering that company {company_name} operates in {markets}
determine if this regulation applies to this company based on the markets it operates in.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_sourcing = "determine if this regulation applies to this company based on the countries it sources from."

prompt_sourcing = '''
Given the following ESG legal document,
and considering that company {company_name} sources from {sourcing}
determine if this regulation applies to this company based on the countries it sources from.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_production = "determine if this regulation applies to this company based on the countries it produces in."

prompt_production = '''
Given the following ESG legal document,
and considering that company {company_name} produces in {production}
determine if this regulation applies to this company based on the countries it produces in.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

search_prompt_offerring_of_financial_products = "determine if this regulation applies to this company based on the products and services it offers."

prompt_products_and_services_offered = '''
Given the following ESG legal document,
and considering that company {company_name} offers the following products and services {products_and_services_offered}
determine if this regulation applies to this company based on the products and services it offers.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
Important: if there is not sufficient or relevant information to make a decision, say unclear. 
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

SEARCH_PROMPT_MAP = {
    "Capital market oriented companies": search_prompt_capital_market_oriented,
    "Number of employees": search_prompt_number_of_employees,
    "Assets": search_prompt_assets,
    "Revenue": search_prompt_revenue,
    "Offering of financial products": search_prompt_offering_of_financial_products,
    "Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)": search_prompt_scope_of_the_REACH,
    "Manufacturers or distributors of batteries": search_prompt_batteries,
    #    "Date of applicability": "",
    "Jurisdiction": search_prompt_jurisdiction,
    "Markets (countries)": search_prompt_markets,
    "Sourcing (countries)": search_prompt_sourcing,
    "Production (Countries)": search_prompt_production,
    "Products and Services offered": search_prompt_offerring_of_financial_products
}

APPLICABILITY_PROMPT_MAP = {
    "Capital market oriented companies": prompt_capital_market_oriented,
    "Number of employees": prompt_number_of_employees,
    "Assets": prompt_assets,
    "Revenue": prompt_revenue,
    "Offering of financial products": prompt_offering_of_financial_products,
    "Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)": prompt_scope_of_the_REACH,
    "Manufacturers or distributors of batteries": prompt_batteries,
    #    "Date of applicability": "",
    "Jurisdiction": prompt_jurisdiction,
    "Markets (countries)": prompt_markets,
    "Sourcing (countries)": prompt_sourcing,
    "Production (Countries)": prompt_production,
    "Products and Services offered": prompt_products_and_services_offered
}

KEY_PARAMETERS = [
    "Capital market oriented companies",
    "Number of employees",
    "Assets",
    "Revenue",
    "Offering of financial products",
    "Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)",
    "Manufacturers or distributors of batteries",
    "Jurisdiction",
    "Markets (countries)",
    "Sourcing (countries)",
    "Production (Countries)",
    "Products and Services offered"
]

KEY_PARAMETERS_TO_VARIABLES_MAP = {
    "Capital market oriented companies": "is_capital_market_oriented",
    "Number of employees": "num_employees",
    "Assets": "assets",
    "Revenue": "revenue",
    "Offering of financial products": "is_offering_financial_products",
    "Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)": "is_REACH",
    "Manufacturers or distributors of batteries": "is_battery",
    "Jurisdiction": "jurisdiction",
    "Markets (countries)": "markets",
    "Sourcing (countries)": "sourcing",
    "Production (Countries)": "production",
    "Products and Services offered": "products_and_services_offered"
}
