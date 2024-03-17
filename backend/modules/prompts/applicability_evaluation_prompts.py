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
Given the following ESG legal document with their regulation name,
and considering that company X is a capital market oriented company
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_number_of_employees = '''
Given the following ESG legal document with its regulation name, and considering that company X has {num_employees} employees determine which of the regulations apply to company X
with respect to number of employees. First Cite the relevant text you used to make your decision and provide your reasoning to see if company X is affected by the regulation based on the number of employees.
Then, say only yes, no, or unclear.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_assets = '''
Given the following ESG legal document with their regulation name, and considering that company X has {assets} in
assets determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_revenue = '''
Given the following ESG legal document with their regulation name, and considering that company X has {revenue} in
revenue determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_offering_of_financial_products = '''
Given the following ESG legal document with their regulation name, and considering that company X offers finantial products
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_scope_of_the_REACH = '''
Given the following ESG legal document with their regulation name, and considering that company X is subject to the REACH regulation
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_batteries = '''
Given the following ESG legal document with their regulation name, and considering that company X is a manufacturer or distributor of batteries
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

#prompt_date_of_applicability = '''
#Given the following ESG legal document with their regulation name, and

prompt_jurisdiction = '''
Given the following ESG legal document with their regulation name, and considering that company X is subject to the jurisdiction of {jurisdiction}
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_markets = '''
Given the following ESG legal document with their regulation name, and considering that company X operates in {markets}
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_sourcing = '''
Given the following ESG legal document with their regulation name, and considering that company X sources from {sourcing}
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_production = '''
Given the following ESG legal document with their regulation name, and considering that company X produces in {production}
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>'''

prompt_products_and_services_offered = '''
Given the following ESG legal document with their regulation name, and considering that company X offers {products_and_services_offered}
determine which of the regulations apply to company X, cite the relevant legal texts for is regulation that applies.
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
    "Date of applicability": "",
    "Jurisdiction": prompt_jurisdiction,
    "Markets (countries)": prompt_markets,
    "Sourcing (countries)": prompt_sourcing,
    "Production (Countries)": prompt_production,
    "Products and Services offered": prompt_products_and_services_offered
}

