import os
import smtplib
from email.message import EmailMessage


def send_password_reset_email(recipient, reset_url):
    server = os.environ['MAIL_SERVER']
    port = int(os.environ.get('MAIL_PORT', '465'))
    username = os.environ['MAIL_USERNAME']
    password = os.environ['MAIL_PASSWORD']
    sender = os.environ.get('MAIL_DEFAULT_SENDER', username)

    message = EmailMessage()
    message['Subject'] = 'lsnuts 密码重置'
    message['From'] = sender
    message['To'] = recipient
    message.set_content(
        '你好，\n\n'
        '我们收到了你的密码重置请求。请在 1 小时内打开以下链接设置新密码：\n\n'
        f'{reset_url}\n\n'
        '如果不是你本人操作，请忽略此邮件。'
    )

    with smtplib.SMTP_SSL(server, port, timeout=15) as smtp:
        smtp.login(username, password)
        smtp.send_message(message)
