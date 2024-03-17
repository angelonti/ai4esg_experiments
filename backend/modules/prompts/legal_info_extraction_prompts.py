key_parameters = '''
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

priming = '''You are a helpful assistant and legal expert that can extract information from legal documents and solve related tasks based only on the provided document.
         You always provide your answer by copying exactly the relevant excerpts from the given document.'''


prompt_key_parameters = '''Given the following ESG legal document determine if it specifies applicability of the law to companies with respect to the following key parameters list:
{key_parameters}
Extract all relevant text excerpts from the document that support the applicability for companies for each key parameter.
The excerpts should give a clear indication of the applicability of the law to the company with respect to the key parameter.
If there is additional criteria for applicability of the law not included in the list above, please specify them by identifying the key parameter name and copying the relevant text excerpts.
Make sure to be as thorough as possible to not miss any relevant information.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>
'''

prompt_requirements_and_penalties = '''Given the following document determine if the document contains information
about the requirements for companies to comply with the law, and penalties for non-compliance.
If the document contains any such information extract all relevant excerpts for the document.
Make sure to be as thorough as possible to not miss any relevant information.
{format_instructions}
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>
'''

