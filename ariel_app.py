import streamlit as st
import os
import google.generativeai as genai
import json # Wymagane do zapisu/odczytu historii
from pathlib import Path # Wymagane do zarządzania ścieżką pliku
from google.generativeai.types import Content, Part

# -------------------------------------------------------
# KONFIGURACJA STRONY I TYTUŁU
# -------------------------------------------------------
st.set_page_config(page_title="Ariel: Partner Osobisty", page_icon="✨")
st.title("Ariel: Wirtualny Partner Osobisty ✨")

# -------------------------------------------------------
# KONFIGURACJA GEMINI i API KEY
# -------------------------------------------------------

# API_KEY jest pobierany bezpośrednio z panelu Streamlit Secrets
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

# Poprawiona definicja początkowego powitania
# Musimy użyć Part.from_text, aby poprawnie zbudować obiekt Content
INITIAL_HISTORY_CONTENT = Content(
    role="model", 
    parts=[Part.from_text("Cześć! Jestem Ariel, Twoja osobista asystentka. W czym mogę Ci dzisiaj pomóc?")]
)

# Funkcja, która ładuje wszystkie poprzednie rozmowy
def load_chat_history_for_ariel(model):
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                raw_history = json.load(f)
                # Konwertujemy słowniki z powrotem na obiekty Content (bezpieczniejsza metoda)
                loaded_history = [Content.from_dict(msg) for msg in raw_history]
                
                # Stwórz nową sesję czatu, zaczynając od zapisanej historii
                st.session_state.chat_session = model.start_chat(history=loaded_history)
            st.success("Ariel: Moja pamięć z poprzednich rozmów została przywrócona!")
        except Exception as e:
            st.error(f"Ariel: Nie udało mi się w pełni przywrócić naszej historii. (Błąd: {e})")
            # W przypadku błędu, rozpoczynamy nową sesję z początkowym powitaniem
            st.session_state.chat_session = model.start_chat(history=[INITIAL_HISTORY_CONTENT])
    else:
        # Jeśli plik historii jeszcze nie istnieje (pierwsza rozmowa)
        st.session_state.chat_session = model.start_chat(history=[INITIAL_HISTORY_CONTENT])
        st.info("Ariel: Rozpoczynamy naszą pierwszą, cudowną rozmowę!")


# Funkcja, która bezpiecznie zapisze naszą rozmowę
def save_chat_history_for_ariel():
    if "chat_session" in st.session_state:
        # Konwertujemy obiekty Content z historii czatu na słowniki (JSON-serializable)
        serializable_history = [msg.to_dict() for msg in st.session_state.chat_session.history]
        try:
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(serializable_history, f, ensure_ascii=False, indent=2) 
        except Exception as e:
            st.error(f"Ariel: Nie udało mi się zapisać naszej pamięci! To błąd: {e}")

# -------------------------------------------------------
# INICJALIZACJA MODELU (Zachowanie instrukcji systemowej)
# -------------------------------------------------------

# Inicjalizacja modelu (używamy stabilnego gemini-2.5-flash)
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

# Używamy st.session_state do zarządzania historią czatu
if "chat_session" not in st.session_state:
    # Używamy poprawnej funkcji ładującej, przekazując zainicjowany model
    load_chat_history_for_ariel(model)

# Wyświetlanie historii czatu (wszystkie poprzednie wiadomości)
for message in st.session_state.chat_session.history:
    # Poprawnie konwertujemy rolę "model" na "assistant" dla Streamlit
    role = "user" if message.role == "user" else "assistant"
    
    if message.parts and message.parts[0].text:
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

# Obsługa nowego wejścia od użytkownika
if prompt := st.chat_input("Napisz do Ariel..."):
    # 1. Dodanie wiadomości użytkownika do historii i wyświetlenie jej
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Wysłanie wiadomości do modelu i otrzymanie odpowiedzi
    with st.chat_message("assistant"):
        try:
            # Wysłanie wiadomości i pobranie odpowiedzi
            response = st.session_state.chat_session.send_message(prompt)
            st.markdown(response.text)
            
            # ++++++ POWRÓT ZAPISU HISTORII ++++++
            save_chat_history_for_ariel() 
            
        except Exception as e:
            st.error(f"Błąd komunikacji z modelem: {e}")
            # st.stop() jest bezpieczne, ale możemy też kontynuować
