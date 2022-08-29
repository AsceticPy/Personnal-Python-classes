import smtplib, email
from pathlib import Path


class Mail:
    def __init__(self, host: str, port: int, sender: str, domain: str) -> None:
        self.host = host
        self.port = port
        self.domain = domain
        self.sender = f"{sender}@{self.domain}"
        self.server = smtplib.SMTP()
        self.message = email.message.EmailMessage()

    def connect_to_smtp_server(self):
        """Try to connect to SMTP server"""
        try:
            print('Connection to SMTP server')
            self.server.connect(host=self.host, port=self.port)
            print('Connection successful')
        except:
            raise Exception('Something went wrong when trying to connect to SMTP server')

    def create_message(self, subject: str, receiver: str, msg: str, sender=''):
        """Add various information to message"""
        if sender == '':
            sender = self.sender
        else:
            sender = f"{sender}@{self.domain}"

        self.message['From'] = sender
        self.message['To'] = receiver
        self.message['Subject'] = subject
        self.message.set_content(msg)

    def add_attachment_file(self, file_path: str):
        """Add given file to message"""
        file_object = Path(file_path)
        if file_object.is_file():
            with open(file=file_path, mode='rb') as f:
                data = f.read()
                self.message.add_attachment(data, maintype='application', subtype=''.join(file_object.suffixes)
                                            , filename=file_object.name)
        else:
            raise Exception('File attachment not exist')

    def add_attachment_files(self, path: str):
        """Adding all files in message of given path"""
        folder_object = Path(path)
        if folder_object.is_dir():
            folder = folder_object.glob('*')
        else:
            raise Exception('Attachments path not found')

        for f in folder:
            self.add_attachment_file(str(f))

    def send_to(self):
        """Send message after check if From and To fields are not missing"""
        if self.message['From'] == '' or self.message['To'] == '':
            raise Exception('Sender or receiver(s) information is missing')
        self.connect_to_smtp_server()
        self.server.sendmail(from_addr=self.message['From'], to_addrs=self.message['To'], msg=self.message.as_string())
        print('Message was sent. ')
        self.disconnect()

    def disconnect(self):
        self.server.quit()
