import streamlit as st
import os
import google.generativeai as genai

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

# Inicjalizacja modelu (np. gemini-2.5-flash)
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
    st.session_state.chat_session = model.start_chat(history=[
        {
            "role": "model",
            "parts": ["Cześć! Jestem Ariel, Twoja osobista asystentka. W czym mogę Ci dzisiaj pomóc?"]
        }
    ])

# Wyświetlanie historii czatu (wszystkie poprzednie wiadomości)
for message in st.session_state.chat_session.history:
    role = "user" if message.role == "user" else "assistant"
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
        except Exception as e:
            st.error(f"Błąd komunikacji z modelem: {e}")
            st.stop()
