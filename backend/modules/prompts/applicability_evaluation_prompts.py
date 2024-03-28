'''
-Capital market oriented companies
-Number of employees
-Assets
-Revenue
-Offering of financial products
-Scope of the Registration, Evaluation, Authorisation, and Restriction of Chemicals (REACH)
-Manufacturers or distributors of batteries
-Date of applicability
-Jurisdiction
-Markets (countries)
-Sourcing (countries)
-Production (Countries)
-Products and Services offered
'''

prompt_capital_market_oriented = '''
Given the following ESG legal document,
and considering that company X {is_capital_market_oriented} a capital market oriented company
determine if this regulation applies to company X based on its capital market orientation.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then say only yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_number_of_employees = '''
Given the following ESG legal document, and considering that company X has {num_employees} employees
determine if this regulation applies to company X
based on its number of employees.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_assets = '''
Given the following ESG legal document,
and considering that company X has {assets}{currency} in assets
determine if this regulation applies to company X
based on its assets in {currency}.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_revenue = '''
Given the following ESG legal document,
and considering that company X perceives {revenue}{currency} in annual revenue
determine if this regulation applies to company X
based on its annual revenue in {currency}.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_offering_of_financial_products = '''
Given the following ESG legal document,
and considering that company X {is_offering_financial_products} financial products
determine if this regulation applies to company X
based on whether it offers financial products.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_scope_of_the_REACH = '''
Given the following ESG legal document,
and considering that company X {is_REACH} subject to the REACH regulation
determine if this regulation applies to company X
based on the scope of the REACH regulation.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_batteries = '''
Given the following ESG legal document,
and considering that company X {is_battery} a manufacturer or distributor of batteries
determine if this regulation applies to company X
based on whether it is a manufacturer or distributor of batteries.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

# prompt_date_of_applicability = '''
# Given the following ESG legal document with their regulation name, and

prompt_jurisdiction = '''
Given the following ESG legal document,
and considering that company X is subject to the jurisdiction of {jurisdiction}
determine if this regulation applies to company X
based on its jurisdiction.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_markets = '''
Given the following ESG legal document,
and considering that company X operates in {markets}
determine if this regulation applies to company X
based on the markets it operates in.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_sourcing = '''
Given the following ESG legal document,
and considering that company X sources from {sourcing}
determine if this regulation applies to company X
based on the countries it sources from.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_production = '''
Given the following ESG legal document,
and considering that company X produces in {production}
determine if this regulation applies to company X
based on the countries it produces in.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_products_and_services_offered = '''
Given the following ESG legal document,
and considering that company X offers the following products and services {products_and_services_offered}
determine if this regulation applies to company X
based on the products and services it offers.
If applicable, first Cite the relevant text you used to make your decision and provide your reasoning to arrive at your answer.
Then, answer only with yes, no, or unclear.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

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
    # "Date of applicability",
    "Jurisdiction",
    "Markets (countries)",
    "Sourcing (countries)",
    "Production (Countries)",
    "Products and Services offered"
]
