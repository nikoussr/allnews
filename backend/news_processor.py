from langchain_community.llms import LlamaCpp

from configs import LLAMA_MODEL_PATH

llm = LlamaCpp(model_path=LLAMA_MODEL_PATH, n_ctx=2048)


def process_news(title, description):
    prompt = f"""
    Ты - аналитик новостей. Твоя задача:
    - Оценить важность новости по шкале от 1 до 10.
    - Добавить теги: спорт, политика, экономика и т.д.
    - Кратко пересказать.

    Новость: {title}
    Описание: {description}

    Ответ:
    """
    return llm.invoke(prompt)
