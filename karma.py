from errbot import BotPlugin, botcmd, re_botcmd
from datetime import datetime
import re


class Karma(BotPlugin):
    """Plugin to give karma to an individual"""

    def update_karma(self, username, count=1):
        """Updates db with current count"""

        username = str(username)

        try:
            current_count = self.get(username).get('karma', 0)
            new_count = current_count + count
        except AttributeError:
            self[username] = {}
            new_count = count

        self.log.debug('new kudo count is {}'.format(new_count))

        self[username] = {
            'time': datetime.now(),
            'karma': new_count,
        }

    @re_botcmd(pattern=r'[\w-]+\+\+', prefixed=False, flags=re.IGNORECASE)
    def give_karma(self, msg, match):
        """This gives karma"""
        if match:
            line = match.group(0)
            username = line.split(' ')[0].rstrip('++')
            self.update_karma(username)

            t = msg.frm.room if msg.is_group else msg.frm
            self.send(t,
                      'karma -- {}: {}'.format(username, self.get(username).get('karma')),
                      in_reply_to=msg,
                      groupchat_nick_reply=True)

    @re_botcmd(pattern=r'[\w-]+\-\-', prefixed=False, flags=re.IGNORECASE)
    def remove_karma(self, msg, match):
        """This removes karma"""
        if match:
            line = match.group(0)
            username = line.split(' ')[0].rstrip('--')
            self.update_karma(username, count=-1)

            t = msg.frm.room if msg.is_group else msg.frm
            self.send(t,
                      'karma -- {}: {}'.format(username, self.get(username).get('karma')),
                      in_reply_to=msg,
                      groupchat_nick_reply=True)
    
    @botcmd(admin_only=True)
    def karma_delete_entries(self, msg, args):
        """Deletes all entries for a user"""
        username = str(args)

        try:
            del self[username]
            text = 'Entries deleted for {} user'.format(username)
        except KeyError:
            text = 'User {} has no entries'.format(username)

        t = msg.frm.room if msg.is_group else msg.frm
        self.send(t,
                  text,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)

    @botcmd
    def karma_list(self, msg, args):
        """Returns a list of users that have a kudo"""
        user_list = []
        for user in self.keys():
            user_list.append('{}:{}'.format(user, self.get(user).get('karma')))

        if user_list == []:
            response = 'No users'
        else:
            response = ', '.join(user_list)

        t = msg.frm.room if msg.is_group else msg.frm
        self.send(t,
                  response,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)

    @botcmd
    def karma(self, msg, args):
        """A way to see your karma stats
            Example:
                !karma <username>
        """
        username = str(args)

        t = msg.frm.room if msg.is_group else msg.frm
        if username == '':
            self.send(t,
                      'Username is required.',
                      in_reply_to=msg,
                      groupchat_nick_reply=True)
            return

        try:
            count = self.get(username).get('karma')
        except (TypeError, NameError, AttributeError):
            count = 0

        self.send(t,
                  '{} has {} kudo points.'.format(username, count),
                  in_reply_to=msg,
                  groupchat_nick_reply=True)
