"""
Pylint checker for the format of the docstrings of filters.

A filter's docstring should have the following structure:

1. Description: Any non-empty text followed by a blank line.
2. Filter Type: A line that starts with "Filter Type:".
3. Trigger: A line that starts with "Trigger:".
"""

import re

from pylint.checkers import BaseChecker, utils

from edx_lint.pylint.common import BASE_ID


def register_checkers(linter):
    """
    Register checkers.
    """
    linter.register_checker(FiltersDocstringFormatChecker(linter))


class FiltersDocstringFormatChecker(BaseChecker):
    """Pylint checker for the format of the docstrings of filters."""

    name = "docstring-format-checker"

    DOCSTRING_MISSING_PURPOSE = "filter-docstring-missing-purpose"
    DOCSTRING_MISSING_TYPE = "filter-docstring-missing-type"
    DOCSTRING_MISSING_TRIGGER = "filter-docstring-missing-trigger"

    msgs = {
        ("E%d91" % BASE_ID): (
            "Filter's (%s) docstring is missing the required purpose section or is badly formatted",
            DOCSTRING_MISSING_PURPOSE,
            "filters docstring is missing the required purpose section or is badly formatted",
        ),
        ("E%d92" % BASE_ID): (
            "Filter's (%s) docstring is missing the required type section or is badly formatted",
            DOCSTRING_MISSING_TYPE,
            "filters docstring is missing the required type section or is badly formatted",
        ),
        ("E%d93" % BASE_ID): (
            "Filter's (%s) docstring is missing the required trigger section or is badly formatted",
            DOCSTRING_MISSING_TRIGGER,
            "filters docstring is missing the required trigger section or is badly formatted",
        ),
    }

    options = ()

    @utils.only_required_for_messages(
        DOCSTRING_MISSING_PURPOSE,
        DOCSTRING_MISSING_TYPE,
        DOCSTRING_MISSING_TRIGGER,
    )
    def visit_classdef(self, node):
        """
        Visit a class definition and check its docstring.

        If the class is a subclass of OpenEdxPublicFilter, check the format of its docstring. Skip the
        OpenEdxPublicFilter class itself.

        """
        if not node.is_subtype_of("openedx_filters.tooling.OpenEdxPublicFilter"):
            return

        if node.name == "OpenEdxPublicFilter":
            return

        docstring = node.doc_node.value if node.doc_node else ""
        if not (error_messages := self._check_docstring_format(docstring)):
            return
        for error_message in error_messages:
            self.add_message(error_message, node=node, args=(node.name,))

    def _check_docstring_format(self, docstring):
        """
        Check the format of the docstring for errors and return a list of error messages.

        The docstring should have the following structure:
        1. Description: Any non-empty text followed by a blank line.
        2. Filter Type: A line that starts with "Filter Type:".
        3. Trigger: A line that starts with "Trigger:".

        For example:

        ```
        Description:
        Filter used to modify the certificate rendering process.

        ... (more description)

        Filter Type:
            org.openedx.learning.certificate.render.started.v1

        Trigger:
            - Repository: openedx/edx-platform
            - Path: lms/djangoapps/certificates/views/webview.py
            - Function or Method: render_html_view
        ```
        """
        required_sections = [
            (r"Purpose:\s*.*\n", self.DOCSTRING_MISSING_PURPOSE),
            (r"Filter Type:\s*.*\n", self.DOCSTRING_MISSING_TYPE),
            (
                r"Trigger:\s*(NA|-\s*Repository:\s*[^\n]+\s*-\s*Path:\s*[^\n]+\s*-\s*Function\s*or\s*Method:\s*[^\n]+)",
                self.DOCSTRING_MISSING_TRIGGER,
            ),
        ]
        error_messages = []
        for pattern, error_message in required_sections:
            if not re.search(pattern, docstring, re.MULTILINE):
                error_messages.append(error_message)
        return error_messages
