import os
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
        f"Kedves Játékos!\n\n"
        f"A(z) '{jatek_cim}' nevű vitajátékban te kerültél sorra érvelésre!\n"
        f"Kérlek lépj be a játékba, és oszdd meg véleményed.\n\n"
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

async def send_game_started_notification(to_emails: list, jatek_cim: str):
    #Környezeti változó, élesben majd a hosting felülettől jönnek
    smtp_server = os.getenv("SMTP_SERVER", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", 1025))
    sender_email = os.getenv("SENDER_EMAIL", "noreply@vitajatek.hu")
    sender_password = os.getenv("SENDER_PASSWORD", "")

    for email in to_emails:
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = f"ELindult a játék! - {jatek_cim}"
        msg.set_content(
            f"Kedves Játékos!\n\n"
            f"A(z) {jatek_cim} című vitajátékot a játékmester elindította.\n"
            f"Kérlek lépj be a játékba és töltsd ki az előzetes kérdőívet!\n\n"
            f"Üdvözlettel,\nA vitajáték rendszere"
        )

        try:
            if not sender_password and smtp_server == "localhost":
                print(f"[EMAIL SIMULATION] Játék indulás kiküldve -> {email}")
            else:
                await aiosmtplib.send(
                    msg,
                    hostname = smtp_server,
                    port = smtp_port,
                    username = sender_email,
                    password = sender_password,
                )
        except Exception as e:
            print(f"Hiba az 'játék elindult' email küldése során: {email}: {e}")

async def send_game_ended_notification(to_emails: list, jatek_cim: str):
    #Környezeti változó, élesben majd a hosting felülettől jönnek
    smtp_server = os.getenv("SMTP_SERVER", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", 1025))
    sender_email = os.getenv("SENDER_EMAIL", "noreply@vitajatek.hu")
    sender_password = os.getenv("SENDER_PASSWORD", "")

    for email in to_emails:
        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = f"Játék lezárva! - {jatek_cim}"
        msg.set_content(
            f"Kedves Játékos!\n\n"
            f"A(z) {jatek_cim} című vitajáték fő szakaszát a játékmester.\n"
            f"Kérlek lépj be a játékba és töltsd ki a záró kérdőívet és add le díj-szavazatodat!\n\n"
            f"Üdvözlettel,\nA vitajáték rendszere"
        )

        try:
            if not sender_password and smtp_server == "localhost":
                print(f"[EMAIL SIMULATION] Játék lezárás kiküldve -> {email}")
            else:
                await aiosmtplib.send(
                    msg,
                    hostname = smtp_server,
                    port = smtp_port,
                    username = sender_email,
                    password = sender_password,
                )
        except Exception as e:
            print(f"Hiba az 'játék lezárva' email küldése során: {email}: {e}")

async def send_round_ended_notification(to_email: str, jatek_cim: str, kor: int):
    #Környezeti változó, élesben majd a hosting felülettől jönnek
    smtp_server = os.getenv("SMTP_SERVER", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", 1025))
    sender_email = os.getenv("SENDER_EMAIL", "noreply@vitajatek.hu")
    sender_password = os.getenv("SENDER_PASSWORD", "")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = f"Egy kör véget ért! - {jatek_cim}"
    msg.set_content(
        f"Kedves Játékmester!\n\n"
        f"A(z) {jatek_cim} című vitajátékod {kor}. köre véget ért (mindenki érvelt és értékelt).\n"
        f"Kérlek lépj be a játék kezelőfelületére, és és indítsd el a következő kört vagy zárd le a játékot!\n\n"
        f"Üdvözlettel,\nA vitajáték rendszere"
    )

    try:
        if not sender_password and smtp_server == "localhost":
            print(f"[EMAIL SIMULATION] Kör vége értesítés a játékmesternek -> {to_email}")
        else:
            await aiosmtplib.send(
                msg,
                hostname = smtp_server,
                port = smtp_port,
                username = sender_email,
                password = sender_password,
                use_tls = (smtp_server == 465),
                start_tls = (smtp_server == 587),
            )
    except Exception as e:
        print(f"Hiba a játékmester 'kör véget ért' értesítése során: {e}")

async def send_ready_for_summary_notification(to_email: str, jatek_cim: str):
    #Környezeti változó, élesben majd a hosting felülettől jönnek
    smtp_server = os.getenv("SMTP_SERVER", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", 1025))
    sender_email = os.getenv("SENDER_EMAIL", "noreply@vitajatek.hu")
    sender_password = os.getenv("SENDER_PASSWORD", "")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = f"A játék készen áll az összegzésre! - {jatek_cim}"
    msg.set_content(
        f"Kedves Játékmester!\n\n"
        f"A(z) {jatek_cim} című vitajátékodban minden játékos kitöltötte a záró kérdőívet és leadta a szavazatát a díjakra.\n"
        f"A játék mostmár készen áll az adatok összegzésére.\n\n"
        f"Üdvözlettel,\nA vitajáték rendszere"
    )
    try:
        if not sender_password and smtp_server == "localhost":
            print(f"[EMAIL SIMULATION] Összesítésre kész értesítés a játékmesternek -> {to_email}")
        else:
            await aiosmtplib.send(
                msg,
                hostname = smtp_server,
                port = smtp_port,
                username = sender_email,
                password = sender_password,
                use_tls = (smtp_server == 465),
                start_tls = (smtp_server == 587),
            )
    except Exception as e:
        print(f"Hiba a játékmester 'összesítésre kész' értesítése során: {e}")