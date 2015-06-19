"""Helper methods and classes."""


from collections import defaultdict
from datetime import timedelta, tzinfo
from .const import FARCY_COMMENT_START, NUMBER_RE

IS_FARCY_COMMENT = FARCY_COMMENT_START.split('v')[0]


def added_lines(patch):
    """Return a mapping of added line numbers to the patch line numbers."""
    added = {}
    lineno = None
    position = 0
    for line in patch.split('\n'):
        if line.startswith('@@'):
            lineno = int(NUMBER_RE.match(line.split('+')[1]).group(1))
        elif line.startswith(' '):
            lineno += 1
        elif line.startswith('+'):
            added[lineno] = position
            lineno += 1
        elif line == "\ No newline at end of file":
            continue
        else:
            assert line.startswith('-')
        position += 1
    return added


def extract_issues(text):
    """Extract farcy violations from a text."""
    if not is_farcy_comment(text):
        return []
    # Strip out start of bullet point, ignore first line
    return [line[2:] for line in text.split('\n')[1:]]


def filter_comments_from_farcy(comments):
    """Filter comments for farcy comments."""
    return (comment for comment in comments if is_farcy_comment(comment.body))


def filter_comments_by_path(comments, path):
    """Filter a comments iterable by a file path."""
    return (comment for comment in comments if comment.path == path)


def is_farcy_comment(text):
    """Return boolean if text was generated by Farcy."""
    return text.startswith(IS_FARCY_COMMENT)


def issues_by_line(comments, path):
    """Return a dictionary mapping line nr to a list of issues for a path."""
    by_line = defaultdict(list)
    for comment in filter_comments_by_path(comments, path):
        issues = extract_issues(comment.body)
        if issues:
            by_line[comment.position].extend(issues)
    return by_line


def subtract_issues_by_line(by_line, by_line2):
    """Return a dict with all issues in by_line that are not in by_line2."""
    result = {}
    for key, values in by_line.items():
        exclude = by_line2.get(key, [])
        filtered = [value for value in values if value not in exclude]
        if filtered:
            result[key] = filtered
    return result


class UTC(tzinfo):

    """Provides a simple UTC timezone class.

    Source: http://docs.python.org/release/2.4.2/lib/datetime-tzinfo.html

    """

    dst = lambda x, y: timedelta(0)
    tzname = lambda x, y: 'UTC'
    utcoffset = lambda x, y: timedelta(0)
