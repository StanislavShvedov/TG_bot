from translate import Translator

def translate_text(text, from_lang='ru', to_lang='en'):
    translator = Translator(from_lang=from_lang, to_lang=to_lang)
    try:
        # Пытаемся перевести текст
        translated_text = translator.translate(text)
        return translated_text  # Возвращаем переведенный текст
    except Exception as e:
        # Если возникает ошибка, возвращаем сообщение об ошибке
        return f"Error: {e}"
