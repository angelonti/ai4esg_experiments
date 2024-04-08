prompt_summary_penalties = """As a professional summarizer, write a concise summary of the following legal document related to penalties for non-compliance.
The summary should only talk about the penalties for non-compliance and nothing else. Make sure to not miss any relevant information. 
1. Rely strictly on the provided document, without including any external information.
2. The summary should only talk about the penalties for companies in case of non-compliance with the law and nothing else.
3. The summary must be concise and to the point, without missing any penalties for non-compliance with the law.
4. Give your results in bullet points.

<BEGIN DOCUMENT>{text}<END DOCUMENT>

CONCISE SUMMARY:
"""

prompt_summary_requirements = """As a professional summarizer, write a concise summary of the following legal document related to requirements for companies to be compliant with the law.
Adhere to the following guidelines:
1. Rely strictly on the provided document, without including any external information.
2. The summary should only talk about the requirements for companies to be compliant with the law and nothing else.
3. The summary must be concise and to the point, without missing any requirements for companies to be compliant with the law.
4. Give your results in bullet points.

<BEGIN DOCUMENT>{text}<END DOCUMENT>

CONCISE SUMMARY:
"""

