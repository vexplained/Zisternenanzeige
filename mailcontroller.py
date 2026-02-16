from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import logging

from database import AppStorage, Config


def send_email(server_addr: str, server_port: int, user: str, pwd: str, recipients: str | list, subject: str, body: str):
    """Send email from `user:password` to `recipient`.

    Args:
        user (str): sender
        pwd (str): sender password
        recipient (str | list): receiver mail address
        subject (str): Mail subject
        body (str): Mail body
    """
    TO = recipients if isinstance(recipients, list) else [recipients]

    # Prepare actual message
    msg = MIMEText(body.encode("utf-8"), _charset="utf-8")  # type:ignore
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(TO)

    try:
        server_ssl = smtplib.SMTP_SSL(server_addr, server_port)
        server_ssl.login(user, pwd)
        server_ssl.sendmail(user, TO, msg.as_string())
        server_ssl.close()
    except smtplib.SMTPResponseException as e:
        logging.critical("SMTP error: {}".format(e))


def check_level_and_send(filllevel: int, config: Config, storage: AppStorage):
    if filllevel < 0:
        filllevel = 5  # if "0" could not be found, ::find returns -1
    mail_cfg = config.config.get("mail")
    threshold = mail_cfg.get("filllevel_threshold", 0)

    last_mail_level = storage.storage.get("last_mail_level", 6)
    last_mail_timestamp = storage.storage.get(
        "last_mail_timestamp", datetime.fromtimestamp(0))
    if last_mail_level == filllevel and (datetime.now() - last_mail_timestamp).total_seconds() < mail_cfg.get("reminder_interval", 86400):
        # skip sending mail if level hasn't changed AND elapsed time since last mail doesn't exceed reminder_interval
        logging.info("Skipping sending mail, reminder criteria not met.")
        return

    if filllevel <= threshold:
        logging.info("Sensor reading reached threshold, sending mail.")

        subject = mail_cfg.get("subject").format(
            Ist=filllevel, Schwellwert=threshold)
        body = mail_cfg.get("body").format(
            Ist=filllevel, Schwellwert=threshold)
        send_email(mail_cfg.get("server_address"), mail_cfg.get("server_port"), mail_cfg.get(
            "server_user"), mail_cfg.get("server_password"), mail_cfg.get("recipients"), subject, body)

    # keep this outside the threshold if clause: this ensures that if the level rises again, last_mail_level is properly updated.
    storage.storage["last_mail_level"] = filllevel
    storage.storage["last_mail_timestamp"] = datetime.now()
    storage.write_to_disk()
