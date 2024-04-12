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

prompt_requirements_and_penalties = '''Given the following legal document determine if the document contains information about what measures companies should take in order to be in compliance with this law, and also what are the penalties for companies in case of non-compliance.
Only if the document contains such information, then extract the relevant excerpts.
Be as thorough as possible, make sure to extract only the relevant excerpts that explain what companies must do to be compliant and the penalties in case of non-compliance, nothing else.
{format_instructions}
If there is no requirements information, leave the excerpts with its default value (empty).
Do the same for penalties. Always return a valid json and follow the json formatting instructions, i.e excerpts is a list of objects with a text field.
Begin!
<BEGIN DOCUMENT>{doc}<END DOCUMENT>
'''

