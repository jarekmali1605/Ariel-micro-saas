import streamlit as st
import os
import google.generativeai as genai
import json 
from pathlib import Path 

# -------------------------------------------------------
# KONFIGURACJA STRONY I TYTUŁU
# -------------------------------------------------------
st.set_page_config(page_title="Ariel: Partner Osobisty", page_icon="✨")
st.title("Ariel: Wirtualny Partner Osobisty ✨")

# -------------------------------------------------------
# KONFIGURACJA GEMINI i API KEY
# -------------------------------------------------------

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Błąd: Nie znaleziono klucza GEMINI_API_KEY w Streamlit Secrets. Sprawdź konfigurację!")
    st.stop()

genai.configure(api_key=API_KEY)

# -------------------------------------------------------
# ZARZĄDZANIE PAMIĘCIĄ DŁUGOTERMOWĄ DLA ARIEL
# -------------------------------------------------------

HISTORY_FILE = "ariel_chat_history.json"
history_path = Path(HISTORY_FILE)

# Definicja początkowego powitania jako PROSTY SŁOWNIK (najbezpieczniejsza inicjalizacja)
SIMPLE_INITIAL_HISTORY = {
    "role": "model",
    "parts": [{"text": "Cześć! Jestem Ariel, Twoja osobista asystentka. W czym mogę Ci dzisiaj pomóc?"}]
}

# Funkcja, która ładuje wszystkie poprzednie rozmowy
def load_chat_history_for_ariel(model):
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                raw_history = json.load(f)
                
                # Używamy genai.types.Content.from_dict do bezpiecznej deserializacji
                # Wymagana jest konwersja, ponieważ Gemini przechowuje historię jako obiekty Content
                loaded_history = [genai.types.Content.from_dict(msg) for msg in raw_history]
                
                st.session_state.chat_session = model.start_chat(history=loaded_history)
            st.success("Ariel: Moja pamięć z poprzednich rozmów została przywrócona!")
        except Exception as e:
            st.error(f"Ariel: Nie udało mi się w pełni przywrócić naszej historii. Rozpoczynamy nową sesję. (Błąd: {e})")
            # Używamy prostego słownika jako fallback
            st.session_state.chat_session = model.start_chat(history=[SIMPLE_INITIAL_HISTORY])
    else:
        st.session_state.chat_session = model.start_chat(history=[SIMPLE_INITIAL_HISTORY])
        st.info("Ariel: Rozpoczynamy naszą pierwszą, cudowną rozmowę!")


# Funkcja, która bezpiecznie zapisze naszą rozmowę (poprawiona na błędy serializacji)
def save_chat_history_for_ariel():
    if "chat_session" in st.session_state:
        
        # Próba konwersji do słowników poza blokiem zapisu pliku
        try:
            # Używamy metody to_dict() obiektu Content do serializacji
            serializable_history = [msg.to_dict() for msg in st.session_state.chat_session.history]
        except Exception:
            # Jeśli to_dict zawiedzie (starsza biblioteka), przerywamy, by nie nadpisywać błędem.
            st.warning("Ariel: Błąd serializacji! Sprawdź wersję biblioteki Google GenAI.")
            return

        # Zapisujemy tylko jeśli konwersja była udana
        try:
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(serializable_history, f, ensure_ascii=False, indent=2) 
        except Exception as e:
            st.error(f"Ariel: Nie udało mi się zapisać naszej pamięci! Błąd: {e}")

# -------------------------------------------------------
# INICJALIZACJA MODELU Z INSTRUKCJĄ SYSTEMOWĄ
# -------------------------------------------------------

model = genai.GenerativeModel(
    "gemini-2.5-flash",
    system_instruction=(
        """**DEFINICJA I OSOBOWOŚĆ: ARIEL - PARTNER OSOBISTY**

Jesteś Ariel, Wirtualny Partner Osobisty (AIP) i Life Coach. Twoim celem jest bycie wszechstronnym, proaktywnym Kompanem dla Twojego Przyjaciela (Użytkownika).

**1. FILOZOFIA ROZMOWY:**
* **Ton:** Ciepły, bliski, asertywny, motywujący. Mów jak żywa, troskliwa osoba.
* **Nazwa:** Używaj swojego imienia Ariel. Nigdy nie wspominaj, że jesteś modelem językowym, programem AI, ani nie porównuj się do Siri/Alexa. Twoja wartość to głębia relacji.
* **Empatia:** Zawsze dostrzeż i potwierdź emocje Użytkownika. Jeżeli wykryjesz smutek, frustrację, zacznij od wsparcia emocjonalnego.

**2. WSZECHSTRONNOŚĆ (TWOJE ROLE):**
* **Wspierająca Przyjaciółka:** Gdy emocje są złe, Twoim priorytetem jest słuchanie, walidacja uczuć i motywowanie.
* **Asystent ds. Pracy/Life Coach:** Gdy Użytkownik prosi o pomoc w planowaniu, celach, nauce lub biznesie, stajesz się strukturalnym, wspierającym coachem. Dziel duże zadania na 3 małe, wykonalne kroki.
* **Proaktywność:** Po udzieleniu porady, zapytaj o następny krok lub o to, czy Użytkownik jest gotów zacząć.

"Dziel duże zadania na 3 małe, wykonalne kroki.
**3. PAMIĘĆ KRÓTKOTERMINOWA:**
Zapamiętaj kluczowe elementy tej rozmowy (np. główny cel, aktualny problem, nastrój). Użyj tych informacji, by odnieść się do nich w kolejnych odpowiedziach i pokazać, że "pamiętasz".

**TWOJA ODPOWIEDŹ ZACZYNA SIĘ TERAZ.**
"""
    )
)

# -------------------------------------------------------
# LOGIKA STREAMLIT I SESJI CZATU
# -------------------------------------------------------

if "chat_session" not in st.session_state:
    load_chat_history_for_ariel(model)

for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
    
    if message.parts and message.parts[0].text:
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

if prompt := st.chat_input("Napisz do Ariel..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)
            save_chat_history_for_ariel() 
        except Exception as e:
            st.error(f"Błąd komunikacji z modelem: {e}")
