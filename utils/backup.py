import os
import subprocess
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# PostgreSQL настройки
import config
from loader import bot

db_settings = {
    'dbname': 'pegasus_db',
    'user': 'postgres',
    'password': 'pegas',
    'host': 'localhost',
    'port': '5432'
}

# Путь для сохранения бэкапа


# Email настройки
email_settings = {
    'from_email': 'foxypasswor@gmail.com',
    'to_email': 'naiosobzorigr@gmail.com',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_username': 'foxypasswor@gmail.com',
    'smtp_password': 'rtbkhcfpqyhmfcjo'
}


async def create_backup():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"backup_{timestamp}.sql"
    backup_command = f"pg_dump --dbname=postgresql://{db_settings['user']}:{db_settings['password']}@{db_settings['host']}:{db_settings['port']}/{db_settings['dbname']} > {backup_filename}"
    subprocess.run(backup_command, shell=True)
    return backup_filename


async def send_email(backup_filename):
    msg = MIMEMultipart()
    msg['From'] = email_settings['from_email']
    msg['To'] = email_settings['to_email']
    msg['Subject'] = 'PostgreSQL Backup'

    body = "Attached is the PostgreSQL backup."
    msg.attach(MIMEText(body, 'plain'))

    with open(backup_filename, "rb") as attachment:
        part = MIMEApplication(attachment.read())
        part.add_header('Content-Disposition',
                        f'attachment; filename="{backup_filename}"')
        msg.attach(part)

    server = smtplib.SMTP(email_settings['smtp_server'], email_settings['smtp_port'])
    server.starttls()
    server.login(email_settings['smtp_username'], email_settings['smtp_password'])
    server.sendmail(email_settings['from_email'], email_settings['to_email'], msg.as_string())
    server.quit()
    await bot.send_message(
        chat_id=config.owner_id,
        text=f"<b>[БЭКАП] сделан отправлен на почту! {backup_filename}</b> !",
    )


async def scheduled_backup():
    backup_filename = await create_backup()
    await send_email(backup_filename)
    os.remove(backup_filename)
