import email
import smtplib, ssl


class _EmailUtil(object):

    def __init__(self, logger, sender, passwd, ls=[], text="Hola", sede="-", attachment=[], stmp_server="smtp.gmail.com", stmp_port=587 ):

        self.log        = logger
        self.em_smtp    = stmp_server
        self.em_port    = stmp_port
        self.em_sender  = sender
        self.em_passwd  = passwd

        self.em_subject = subject
        self.em_text    = text
        self.em_targets = ls
        self.em_attach  = attachment
        self.em_sede    = sede

        self.em_cont    = None


    def _em_gmail(self):

        if type(self.em_targets) is not list:
            self.em_targets = list(self.em_targets)

        context = ssl.create_default_context()
        self.em_cont = f"Subject: {self.subject}\n\n{self.text}"

        try:
            server = smtplib.SMTP(self.em_smtp, self.em_port)
            server.ehlo() # Can be omitted
            server.starttls(context=context) # Secure the connection
            server.ehlo() # Can be omitted
            server.login(self.em_sender, self.em_passwd)
            server.sendmail(self.em_sender, self.em_targets, self.em_subject)
        except Exception as e:
            # Print any error messages to stdout
            self.log.error(f"Error send EMAIL - {e}")
        finally:
            server.quit()
            self.log.info(f"Cerrando conexion EMAIL")
