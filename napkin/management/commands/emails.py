import datetime
import os
import requests
from django.core.management.base import BaseCommand
from napkin.models import Group

class Command(BaseCommand):
    """ A script to send email messages to subscribed users. """
    MAILGUN_URL = 'https://api.mailgun.net/v3/notify.thisisnapkin.com/messages'
    MAILGUN_API_KEY = ('api', os.environ.get('MAILGUN_API_KEY', 'YOUR_API_KEY'))
    EMAIL_FROM = 'NAPKIN <notify@thisisnapkin.com>'

    help = 'Send emails to subscribed users.'

    @staticmethod
    def send_email(recipients, subject, body):
        """ Send an email message using Mailgun. """
        data = {'from': Command.EMAIL_FROM, 'to': recipients, 'subject': subject, 'html': body}
        return requests.post(url=Command.MAILGUN_URL, auth=Command.MAILGUN_API_KEY, data=data)

    def handle(self, *args, **options):
        three_days_ago = datetime.datetime.now() - datetime.timedelta(days=3)

        for group in Group.objects.all():
            subscribers = group.subscribers.all()
            if not subscribers:
                continue

            posts = group.post_set.filter(created__gt=three_days_ago)
            if not posts:
                continue

            subject = 'Here is your napkin digest for group [{group}]!'.format(group=group.name)
            email_date = datetime.datetime.now()
            email_date = email_date.strftime("%B %d, %Y")
            subject = subject + " -- " + email_date

            urls = ''
            for p in posts:
                post_url = 'http://www.thisisnapkin.com/click/' + str(p.id) + '/redirect/'

                if p.text:
                    text = '<div style="color: #989898;>' + p.text + '</div><br/>'
                else:
                    text = '<span style="color: #989898;>' + 'bla' + '</span><br/>'

                urls = '<a style="font-size: 16px;line-height: 1.8em;" href="' + post_url + '">' + p.title + '</a><br/>' + p.text + '<br/>' + '<div style="color: #989898;font-weight: bold;">' + str(p.hits) + ' hits</div><br/><br/>' + urls

            body = '<html><head><meta charset = "UTF-8" /></head><body>' + urls + '</body></html>'

            for subscriber in subscribers:
                resp = Command.send_email(recipients=[subscriber.email], subject=subject, body=body)
                if resp.status_code != 200:
                    self.stdout.write(self.style.ERROR('Failed sending to group [{group}].'.format(group=group.name)))
                    self.stderr.write('{code} | {text}'.format(code=resp.status_code, text=resp.text))
                    break
            else:
                self.stdout.write(self.style.SUCCESS('Sent emails to group [{group}].'.format(group=group.name)))
