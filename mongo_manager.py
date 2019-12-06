from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import datetime
import subprocess


class MongoManager:

    """

    """

    def __init__(self,
                 to_addrs):

        self.to_addrs = to_addrs

    def _send_alert_email(self, to_addr):
        """ A small util that sends a single email message through TRG's email server.
        This method should only be used for one email at a time. The main email sending
        method 'send_alerts' will loop through the to_addrs attribute of the Class.

        Args:
            to_addr (str): a single email

        Returns:
            nothing.
        """

        # Default from_adr
        from_addr = "QuadraticPythonProcesses@Richards.com"

        # The metadata of the message
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = "Mongo Daemon Down: " + str(datetime.date.today())

        # The body of the email
        message = 'The Mongo Daemon appears to be down'
        msg.attach(MIMEText(message, 'plain'))

        # Connection to the TRG Email Server, Walnut
        server = smtplib.SMTP('walnut.richardsgroup.net')

        # Transforming the email object into text and firing it out
        text = msg.as_string()
        server.sendmail(from_addr, to_addr, text)

        # Closing the connection to the sever, as every good little script should
        server.quit()

    def _send_alerts(self):
        """Just a loop through the Class' to_addrs attribute"""

        for email in self.to_addrs:

            self._send_alert_email(to_addr=email)

    def _retrieve_daemon_status(self):
        """The function that checks the status of the server via a subprocess call"""

        # The check_output() function returns a byte str. In order to search this
        # output for words, we need to convert it to a string
        server_output = str(subprocess.check_output(['service', 'mongod', 'status']))

        if 'active (running)' in server_output:

            return True

        else:

            return False

    def is_mongo_running(self):
        """The main process. Please call this."""

        # First checking to see if the daemon is running
        # If so, simply do nothing
        if self._retrieve_daemon_status():

            return None

        # Else, send out those email alerts
        else:

            self._send_alerts()


watcher = MongoManager(to_addrs=['trevor_mcinroe@richards.com', 'jake_smith@richards.com'])
watcher.is_mongo_running()
