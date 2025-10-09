# users/adapter.py

from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):

    def add_message(self, request, level, message_template, message_context=None, extra_tags=''):
        if message_template == 'account/messages/email_confirmation_sent.txt':
            return
        super().add_message(request, level, message_template, message_context, extra_tags)