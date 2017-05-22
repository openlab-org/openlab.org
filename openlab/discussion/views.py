# django
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.http import Http404


# first party
from openlab.core.generic_views import ViewInfo, RedirectException

# local
from .models import Thread, Message
from .forms import MessageForm, NewThreadForm

def _one_of(val, *options):
    assert not val or val in options or val.strip('-') in options
    return val or options[0]

class ListDiscussionsBase(ViewInfo):
    template_basename = "discussions"
    breadcrumb = _('Discussions')
    PAGE_SIZE = 30

    def get_queryset(self, obj):
        return obj.threads.filter(is_private=False)

    def get_more_context(self, request, obj):
        # Create a new thread (without topic-object, i.e. a "message board"
        # style thread)
        new_thread = Thread()
        new_thread.topic_object = obj
        if request.user.is_authenticated():
            new_thread.user = request.user

        search = {}
        initial = {}
        if request.GET.get('tag'):
            search['tag'] = str(request.GET.get('tag', ''))
            initial['tags'] = [search['tag']]

        form, new_message_created = new_message_form(request, new_thread,
                                        NewThreadForm, obj, initial=initial)

        # URL to this page
        my_url = request.get_full_path()

        if new_message_created:
            # Because of timing issues we need to manually trigger this
            from . import signals # TODO fix this
            signals.trigger_thread_save(new_thread)

            # The return value is a special one signalling that we want to
            # redirect to self to prevent double posting
            raise RedirectException(new_thread.get_absolute_url())

        # Otherwise just display the form

        # Add sortability
        ordering = request.GET.get('ordering', '')
        ordering = _one_of(ordering, "-last_edited", "creation_date",
                                "messages_count", "subscribers_count" "title")

        # And pagination
        page_number = request.GET.get('page', 1)

        # Paginate results
        queryset = self.get_queryset(obj)

        queryset = queryset.annotate(messages_count=Count('messages'))

        if ordering == 'subscribers_count':
            queryset = queryset.annotate(subscribers_count=Count('subscribers'))

        if 'tag' in search:
            # Add tag filtering
            queryset = queryset.filter(tags__name=search['tag'])

        results = queryset.order_by(ordering)
        paginator = Paginator(results, self.PAGE_SIZE)
        page = paginator.page(page_number)

        return {
                'threads': page.object_list,
                'page': page,
                'discussion_tag_url': my_url,
                'new_thread_form': form,
                'thread_view_name': self.thread_view_name,
                'search': search,
            }




def new_message_form(request, thread, form_class, context_object, initial={}):
    """
    Creates a new message form, and also renders / creates the new message (and
    possibly thread) if the form was submitted.
    """
    # Now check if we are doing something
    form = None
    thread_exists = bool(thread.id)
    users = list(thread.subscribers.all()) if thread_exists else []
    new_message_created = False

    if request.user.is_authenticated():
        if request.method == 'POST':
            form = form_class(request.POST,
                        thread_exists=thread_exists,
                        users=users,
                        initial=initial)
            if form.is_valid():
                message = form.save(commit=False)

                # Trigger update in last created, and/or create new 
                form.save_to_thread(thread)
                if not thread_exists and hasattr(context_object, 'threads'):
                    context_object.threads.add(thread)

                # Add message to thread, assign user to thread
                message.thread = thread
                message.user = request.user

                # Generate HTML of comment
                message.regenerate_markdown(context_object)
                message.save()

                # Add user to thread subscribers
                thread.subscribers.add(request.user)
                form = None

                # Successfully submitted!
                new_message_created = True

        # If we submit a form, we want the form displayed on the next page to
        # be "fresh"
        if not form:
            form = form_class(thread_exists=thread_exists,
                            users=users, initial=initial)

    return form, new_message_created


class DiscussableMixin(object):
    """
    Mix-in with a view and then call get_discussion_context somewhere to
    display a discussion thread on another page.
    """
    COMMENT_PAGE_SIZE = 30
    def get_discussion_context(self, request, topic, context_object=None, thread=None):

        # Try getting the thread about this topic --- if it does not exist,
        # create a fake one
        if not thread:
            ctype = ContentType.objects.get_for_model(topic)
            try:
                thread = Thread.objects.get(
                        content_type=ctype,
                        object_id=topic.id,
                        is_private=False)
            except Thread.DoesNotExist:
                thread = Thread()
                thread.topic_object = topic
                if request.user.is_authenticated():
                    thread.user = request.user

        form, new_message_created = new_message_form(request, thread, MessageForm, context_object)

        if new_message_created:
            # The return value is a special one signalling that we want to
            # redirect to self to prevent double posting
            my_url = request.get_full_path()
            raise RedirectException(my_url)

        # Otherwise just display the form

        if not thread.id:
            # No thread yet created
            queryset = Message.objects.none()
        else:
            queryset = Message.objects.filter(thread=thread)

        # Add sortability
        ordering = request.GET.get('ordering', '')
        ordering = _one_of(ordering, "creation_date")

        # And pagination
        page_number = request.GET.get('page', 1)

        if ordering == 'plusones_count':
            queryset = queryset.annotate(plusones_count=Count('plusones'))

        # Paginate results
        results = queryset.order_by(ordering)
        paginator = Paginator(results, self.COMMENT_PAGE_SIZE)
        page = paginator.page(page_number)

        message_list = list(page.object_list)

        return {
                'message_list': message_list,
                'object_list': message_list,
                'thread': thread,
                #'discussion_tag_url': my_url,
                'discussion_tag_url': None,
                'page': page,
                'message_form': form,
            }

class ViewThreadBase(ViewInfo, DiscussableMixin):
    template_basename = "thread"
    breadcrumb = _('Thread')
    PAGE_SIZE = 30

    def get_more_context(self, request, obj):
        thread_id = self.kwargs.get('thread_id')
        try:
            thread = obj.threads.get(id=thread_id)
        except Thread.DoesNotExist:
            return Http404

        return self.get_discussion_context(request, None, obj, thread=thread)

@login_required
def view_thread(request, thread_id, template="discussion/view_thread.html"):
    thread = get_object_or_404(Thread, id=thread_id)
    return render(request, template, {"thread": thread})

