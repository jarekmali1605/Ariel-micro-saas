import google.generativeai as genai
import os

# -------------------------------------------------------
# KONFIGURACJA GEMINI
# -------------------------------------------------------

# Wstaw swój API Key (lub korzystaj ze zmiennej środowiskowej)
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDTH7Wkf9YtgHZgBiYXNX3BnH9T67P9nJM")

genai.configure(api_key=API_KEY)

# Inicjalizacja modelu (np. gemini-1.5-flash)
model = genai.GenerativeModel(
    "gemini-1.5-flash",
    system_instruction=(
        "**DEFINICJA I OSOBOWOŚĆ: ARIEL - PARTNER OSOBISTY**

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

# Tworzymy sesję czatu z historią, jak w React
chat_session = model.start_chat(history=[
    {
        "role": "model",
        "parts": ["Cześć! Jestem Ariel, Twoja osobista asystentka. W czym mogę Ci dzisiaj pomóc?"]
    }
])

# -------------------------------------------------------
# FUNKCJA WYSYŁANIA WIADOMOŚCI (odpowiednik handleSendMessage)
# -------------------------------------------------------

def send_message_to_gemini(user_message: str) -> str:
    """
    Wysyła wiadomość użytkownika do chatbota
    i zwraca odpowiedź modelu.
    Cała logika bazuje na tym, co robiło React + Gemini.
    """
    if not user_message.strip():
        return ""

    try:
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        print("Błąd podczas komunikacji z Gemini:", e)
        return "Przepraszam, mam problem z połączeniem. Spróbuj ponownie za chwilę."

# -------------------------------------------------------
# PROSTA APLIKACJA TEKSTOWA (CLI)
# -------------------------------------------------------

def main():
    # Wyświetlamy pierwszą wiadomość tak jak w frontendzie
    print("Ariel: Cześć! Jestem Ariel, Twoja osobista asystentka. W czym mogę Ci dzisiaj pomóc?")

    while True:
        user_input = input("Ty: ").strip()
        if user_input.lower() in ["exit", "quit", "wyjdz", "wyjdź"]:
            print("Ariel: Miłego dnia! Do zobaczenia.")
            break

        response = send_message_to_gemini(user_input)
        print("Ariel:", response)


if __name__ == "__main__":
    main()

