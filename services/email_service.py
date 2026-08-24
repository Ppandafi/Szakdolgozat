import os
import smtplib

import aiosmtplib
from email.message import EmailMessage

async def send_turn_notification(to_email: str, jatek_cim: str):
    #Környezeti változó, élesben majd a hosting felülettől jönnek
    smtp_server = os.getenv("SMTP_SERVER", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", 1025))
    sender_email = os.getenv("SENDER_EMAIL", "noreply@vitajatek.hu")
    sender_password = os.getenv("SENDER_PASSWORD", "")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = f"Te következel! - {jatek_cim}"

    msg.set_content(
        f"Kedves játékos!\n\n"
        f"A(z) '{jatek_cim}' nevű vitajátékban te kerültél sorra érvelésre!\n"
        f"Kérlek, lépj be a játékba, és oszdd meg véleményed.\n\n"
        f"Üdvözlettel,\n"
        f"A vitajáték rendszere"
    )

    try:
        if not sender_password and smtp_server == "localhost":
            print(f"[EMAIL SIMULATION] Címzett: {to_email} | Tárgy: {msg['Subject']}")
            return True

        #Éles küldés
        await aiosmtplib.send(
            msg,
            hostname = smtp_server,
            port = smtp_port,
            username = sender_email,
            password = sender_password,
            use_tls = (smtp_server == 465),
            start_tls = (smtp_server == 587),
        )
        return True
    except Exception as e:
        print(f"Hiba az értesítő email küldésekor: {e}")
        return False