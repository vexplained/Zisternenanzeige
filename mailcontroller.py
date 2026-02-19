from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
import logging
import socket

from database import AppStorage, Config

logger = logging.getLogger("Mail")


def send_email(server_addr: str, server_port: int, user: str, realname: str, pwd: str, recipients: str | list, subject: str, body: str):
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
    msg["From"] = formataddr((str(Header(realname, 'utf-8')), user))
    msg["To"] = ", ".join(TO)

    try:
        server_ssl = smtplib.SMTP_SSL(server_addr, server_port)
        server_ssl.login(user, pwd)
        server_ssl.sendmail(user, TO, msg.as_string())
        server_ssl.close()
    except smtplib.SMTPResponseException as e:
        logger.critical("SMTP error: {}".format(e))


def check_level_and_send(filllevel: int, config: Config, storage: AppStorage):
    if filllevel < 0:
        filllevel = 5  # if "0" could not be found, ::find returns -1
    cfg_mail = config.config.get("mail")
    threshold = cfg_mail.get("filllevel_threshold", 0)

    last_mail_level = storage.storage.get("last_mail_level", 6)
    last_mail_timestamp = storage.storage.get(
        "last_mail_timestamp", datetime.fromtimestamp(0))
    if last_mail_level == filllevel and (datetime.now() - last_mail_timestamp).total_seconds() < cfg_mail.get("reminder_interval", 86400):
        # skip sending mail if level hasn't changed AND elapsed time since last mail doesn't exceed reminder_interval
        logger.debug("Skipping sending mail, reminder criteria not met.")
        return

    if filllevel <= threshold:
        logger.info("Sending mail: Sensor reading reached threshold.")

        subject = format_mail_str(cfg_mail.get("strings").get(
            "subject"), filllevel, threshold, config)
        body = format_mail_str(cfg_mail.get("strings").get(
            "body"), filllevel, threshold, config)
        cfg_mail_server = cfg_mail.get("server")
        send_email(cfg_mail_server.get("address"), cfg_mail_server.get("port"), cfg_mail_server.get(
            "user"), cfg_mail_server.get("realname"), cfg_mail_server.get("password"), cfg_mail.get("recipients"), subject, body)

    # keep this outside the threshold if clause: this ensures that if the level rises again, last_mail_level is properly updated.
    storage.storage["last_mail_level"] = filllevel
    storage.storage["last_mail_timestamp"] = datetime.now()
    storage.write_to_disk()


def format_mail_str(string: str, filllevel: int, threshold: int, config: Config):
    dict_level_translations = config.config.get(
        "mail").get("strings").get("level_translations")
    return string.format(Ist=filllevel, Schwellwert=threshold,
                         level_translation=dict_level_translations.get(filllevel), URL=f"http://{get_ip()}:5000")


def get_ip():
    """
    Source: https://stackoverflow.com/a/28950776
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP
