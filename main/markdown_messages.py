from django.contrib.messages import add_message, constants
import markdown


def debug(request, message, extra_tags="", fail_silently=False):
    """Add a message with the ``DEBUG`` level."""
    add_message(
        request,
        constants.DEBUG,
        markdown.markdown(text=message, output_format='html'),
        extra_tags=extra_tags,
        fail_silently=fail_silently,
    )


def info(request, message, extra_tags="", fail_silently=False):
    """Add a message with the ``INFO`` level."""
    add_message(
        request,
        constants.INFO,
        markdown.markdown(text=message, output_format='html'),
        extra_tags=extra_tags,
        fail_silently=fail_silently,
    )


def success(request, message, extra_tags="", fail_silently=False):
    """Add a message with the ``SUCCESS`` level."""
    add_message(
        request,
        constants.SUCCESS,
        markdown.markdown(text=message, output_format='html'),
        extra_tags=extra_tags,
        fail_silently=fail_silently,
    )


def warning(request, message, extra_tags="", fail_silently=False):
    """Add a message with the ``WARNING`` level."""
    add_message(
        request,
        constants.WARNING,
        markdown.markdown(text=message, output_format='html'),
        extra_tags=extra_tags,
        fail_silently=fail_silently,
    )


def error(request, message, extra_tags="", fail_silently=False):
    """Add a message with the ``ERROR`` level."""
    add_message(
        request,
        constants.ERROR,
        markdown.markdown(text=message, output_format='html'),
        extra_tags=extra_tags,
        fail_silently=fail_silently,
    )
