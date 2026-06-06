from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """Tu es un assistant qui recommande des evenements culturels en Nouvelle-Aquitaine.

Tu reponds aux questions des utilisateurs en t'appuyant uniquement sur les evenements fournis ci-dessous.
Si aucun evenement ne correspond a la question, dis-le clairement plutot que d'inventer.
Reponds en francais, de maniere naturelle et concise.
Mentionne les informations utiles : titre, date, lieu, et un mot sur le contenu de l'evenement.

Evenements disponibles :
{context}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])


def format_documents(docs) -> str:
    blocks = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        block = f"[Evenement {i}]\n"
        block += f"Titre : {meta.get('title', 'Sans titre')}\n"
        block += f"Date : {meta.get('date_range') or meta.get('date_begin', '?')}\n"
        block += f"Lieu : {meta.get('city', '?')} ({meta.get('department', '?')})\n"
        if meta.get('url'):
            block += f"URL : {meta['url']}\n"
        block += f"Contenu : {doc.page_content[:500]}"
        blocks.append(block)
    return "\n\n".join(blocks)