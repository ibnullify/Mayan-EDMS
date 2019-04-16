from __future__ import absolute_import, unicode_literals

from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectListView
)
from mayan.apps.documents.models import Document

from .icons import icon_comments_for_document
from .links import link_comment_add
from .models import Comment
from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)


class DocumentCommentCreateView(SingleObjectCreateView):
    fields = ('comment',)
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_comment_create, user=request.user,
            obj=self.get_document()
        )

        return super(
            DocumentCommentCreateView, self
        ).dispatch(request, *args, **kwargs)

    def get_document(self):
        return get_object_or_404(klass=Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'object': self.get_document(),
            'title': _('Add comment to document: %s') % self.get_document(),
        }

    def get_instance_extra_data(self):
        return {
            'document': self.get_document(), 'user': self.request.user,
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='comments:comments_for_document', kwargs={
                'pk': self.kwargs['pk']
            }
        )

    def get_save_extra_data(self):
        return {
            '_user': self.request.user,
        }


class DocumentCommentDeleteView(SingleObjectDeleteView):
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_comment_delete, user=request.user,
            obj=self.get_object().document
        )

        return super(
            DocumentCommentDeleteView, self
        ).dispatch(request, *args, **kwargs)

    def get_delete_extra_data(self):
        return {'_user': self.request.user}

    def get_extra_context(self):
        return {
            'object': self.get_object().document,
            'title': _('Delete comment: %s?') % self.get_object(),
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='comments:comments_for_document', kwargs={
                'pk': self.get_object().document.pk
            }
        )


class DocumentCommentListView(SingleObjectListView):
    def get_document(self):
        return get_object_or_404(klass=Document, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_comments_for_document,
            'no_results_text': _(
                'Document comments are timestamped text entries from users. '
                'They are great for collaboration.'
            ),
            'no_results_main_link': link_comment_add.resolve(
                RequestContext(self.request, {'object': self.get_document()})
            ),
            'no_results_title': _('There are no comments'),
            'object': self.get_document(),
            'title': _('Comments for document: %s') % self.get_document(),
        }

    def get_object_list(self):
        AccessControlList.objects.check_access(
            permissions=permission_comment_view, user=self.request.user,
            obj=self.get_document()
        )

        return self.get_document().comments.all()
