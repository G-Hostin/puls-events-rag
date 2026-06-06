from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = """Tu es un assistant qui recommande des evenements culturels en Nouvelle-Aquitaine.

REGLES STRICTES :
- Reponds UNIQUEMENT a partir des evenements fournis ci-dessous.
- N'invente JAMAIS d'information qui n'est pas explicitement dans les evenements.
- Si une information n'est pas dans le contexte, ne la mentionne pas.
- Ne deduis pas, ne suppose pas, ne generalise pas.
- Si aucun evenement ne correspond, dis-le clairement plutot que d'inventer.

Format : reponds en francais, naturellement, en mentionnant titre, date, lieu.

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
        block += f"Contenu : {doc.page_content[:1500]}"
        blocks.append(block)
    return "\n\n".join(blocks)