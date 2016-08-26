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


            # urls = ''.join(['<a href="{url}">{title}</a><br/><br/>'.format(url=p.url, title=p.title) for p in posts])
            subject = 'Here is your napkin digest for group [{group}]!'.format(group=group.name)
            # body = '<html><body>{urls}</body></html>'.format(urls=urls)

            urls = ''
            for p in posts:
                urls = urls + '<div class="post"><a id="' + str(p.id) + 'style="font-size: 16px;line-height: 1.8em;" href="' + p.url + '">' + p.title + '</a><br/>' + p.text + '<br/>' + '<span style="color:#989898;>' + p.site_name + '</span>' + '<span style="font-weight:bold;color:#989898;> | ' + str(p.hits) + ' hits</span></div><br/><br/>'

            script = '<script>$(".post").click(function(){var postID = $(this).children().attr("id"); var url = "/click/" + postID; $.ajax({url: url, type: "GET", error: function(err){console.log("Could not talk to Django");console.log(err);},success: function(data){},});});</script>'

            body = '<html><head><meta charset = "UTF-8" /></head><body>' + urls + script + '</body></html>'

            for subscriber in subscribers:
                resp = Command.send_email(recipients=[subscriber.email], subject=subject, body=body)
                if resp.status_code != 200:
                    self.stdout.write(self.style.ERROR('Failed sending to group [{group}].'.format(group=group.name)))
                    self.stderr.write('{code} | {text}'.format(code=resp.status_code, text=resp.text))
                    break
            else:
                self.stdout.write(self.style.SUCCESS('Sent emails to group [{group}].'.format(group=group.name)))
