import google.generativeai as genai
try:
    from . import config
except ImportError:
    import config
import time

def configure_gemini():
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in configuration.")
    genai.configure(api_key=config.GEMINI_API_KEY)

def get_answer(text_prompt: str, mode: int = 1) -> str:
    """
    Sends text to Gemini with specific prompt mode.
    Mode 1: Short (Max 3 sentences)
    Mode 2: Standard (Current)
    Mode 3: Detailed (5W1H Table)
    """
    try:
        configure_gemini()
        
        # 1. PREPARE PROMPT
        suffix = ""
        if mode == 1:
            prefix = "INSTRUKSI KHUSUS: JAWAB HANYA 1 KALIMAT. JANGAN MEMBERIKAN PENJELASAN."
            suffix = "\n\nINGAT: HANYA 1 KALIMAT SAJA."
        elif mode == 2:
            prefix = "INSTRUKSI KHUSUS: JAWAB MAKSIMAL 3 KALIMAT. LANGSUNG KE INTI."
            suffix = "\n\nINGAT: MAKSIMAL 3 KALIMAT."
        elif mode == 4:
            prefix = "INSTRUKSI KHUSUS: BERIKAN ANALISIS KRITIS DAN MENDALAM. SERTAKAN BUKTI TEORETIS JIKA ADA."
            suffix = "\n\nINGAT: WAJIB KOMPREHENSIF DENGAN STRUKTUR YANG JELAS."
        else:
            # Mode 3 (Default/Standard)
            prefix = "INSTRUKSI KHUSUS: JAWAB DENGAN LUGAS, AKURAT, DAN OBJEKTIF. HINDARI BASA-BASI."
            suffix = "\n\nINGAT: FOKUS PADA INTI PERMASALAHAN."

        final_prompt = f"{prefix}\n\n{text_prompt}\n{suffix}"

        # 2. MODEL ROTATION STRATEGY
        available_models = [
            'gemini-2.5-flash',       # Try Newest
            'gemini-2.0-flash',       # Fallback A
            'gemini-1.5-flash',       # Fallback B
            'gemini-flash-latest'     # Fallback C
        ]
        
        last_error = None
        
        for model_name in available_models:
            print(f"[GEMINI] Connecting to model: {model_name}...")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(final_prompt)
                return response.text
            except Exception as e:
                error_str = str(e)
                # If Quota error, try next.
                if "429" in error_str or "Quota" in error_str or "404" in error_str:
                    print(f"[WARN] Failed with {model_name} ({error_str[:50]}...). Trying next...")
                    last_error = e
                    continue
                else:
                    # Logic or Network Error -> Fail fast
                    return f"API Error: {error_str}"

        # If we get here, all models failed
        return f"ALL Models Failed. Last Error: {str(last_error)}"

    except Exception as e:
        return f"Critical Error: {str(e)}"
