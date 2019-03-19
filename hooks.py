import re
import requests
from urlwatch import filters
from urlwatch import jobs
from urlwatch import reporters


class CleanHtmlFilter(filters.FilterBase):

    __kind__ = 'clean-html'

    def filter(self, data, subfilter=None):
        self._no_subfilters(subfilter)
        return data \
            .replace('\xc2\xad', '') \
            .replace('­', '')


class AHFilter(filters.FilterBase):

    __kind__ = 'ah'

    def filter(self, data, subfilter=None):
        self._no_subfilters(subfilter)

        data = CleanHtmlFilter(self.job, self.state).filter(data)

        parent_selector_parser = filters.LxmlParser('css', '.product', 'selector')
        parent_selector_parser.feed(data)
        lines = []
        for parent_element in parent_selector_parser._get_filtered_elements():
            parent_data = parent_selector_parser._to_string(parent_element)

            description = filters.CssFilter(self.job, self.state).filter(parent_data, '.product-description')
            description = filters.Html2TextFilter(self.job, self.state).filter(description, 're')
            description = ' - '.join([item.strip() for item in description.split('\n')])

            price = filters.CssFilter(self.job, self.state).filter(parent_data, '.product-price')
            price = filters.Html2TextFilter(self.job, self.state).filter(price, 're')
            price = ' - '.join([item.strip() for item in price.split('\n')])
            price = '€%s' % price

            discount = filters.CssFilter(self.job, self.state).filter(parent_data, '.discount-block')
            discount = filters.Html2TextFilter(self.job, self.state).filter(discount, 're')
            discount = ' - '.join([item.strip() for item in discount.split('\n')])

            line = ' | '.join([description, discount, price])
            line = '  → %s' % line
            lines.append(line)

        return '\n'.join(lines)


class CustomReporter(reporters.ReporterBase):

    def submit(self):
        raise NotImplementedError()

    def _get_text(self, line_length=75):
        summary = self._get_summary(line_length)
        details = self._get_details(line_length)

        if summary is None and details is None:
            return None

        text = self._format_text(summary, details, line_length)

        return text

    def _get_summary (self, line_length):
        summary = []
        for job_state in self.report.get_filtered_job_states(self.job_states):
            pretty_name = job_state.job.pretty_name()

            summary_title = '%s: %s' % (job_state.verb.upper(), pretty_name)
            summary_title = self._format_summary_item(summary_title, job_state.verb.upper(), line_length)
            summary.append(summary_title)

        if not summary:
            return None

        summary = self._format_summary(summary, line_length)
        return summary

    def _get_details (self, line_length):
        details = []
        for job_state in self.report.get_filtered_job_states(self.job_states):
            pretty_name = job_state.job.pretty_name()
            location = job_state.job.get_location()
            if pretty_name != location:
                location = '%s (%s)' % (pretty_name, location)

            summary_title = '%s: %s' % (job_state.verb.upper(), location)
            content = self._format_content(job_state, line_length)
            detail = self._format_details_item(summary_title, content, job_state.verb, line_length)
            details.append(detail)

        if not details:
            return None

        details = self._format_details(details, line_length)
        return details

    def _format_text (self, summary, details, line_length):
        if not summary and not details:
            return None
        if not summary:
            return details
        if not details:
            return summary

        return '%s\n\n%s\n' % (summary, details)

    def _format_summary (self, titles, line_length):
        sep = line_length * '='
        return '%s\n%s\n%s' % (sep, '\n'.join(titles), sep)

    def _format_summary_item (self, title, type, line_length):
        return title

    def _format_details_item (self, title, content, type, line_length):
        title = self._format_details_item_title(title, type, line_length)
        content = self._format_details_item_content(content, type, line_length)

        return '%s\n%s' % (title, content)

    def _format_details_item_title (self, title, type, line_length):
        sep = line_length * '-'
        return '%s\n%s\n%s' % (sep, title, sep)

    def _format_details_item_content (self, content, type, line_length):
        if not content:
            content = 'No data to display'
        return content

    def _format_details (self, details, line_length):
        return '\n\n'.join(details)

    def _format_content(self, job_state, line_length):
        if job_state.verb == 'error':
            return job_state.traceback.strip()

        if job_state.verb == 'unchanged':
            return job_state.old_data

        if job_state.old_data in (None, job_state.new_data):
            return None

        return job_state.new_data


class CustomSlackReporter(CustomReporter, reporters.SlackReporter):

    __kind__ = 'custom-slack'

    def submit(self):
        webhook_url = self.config['webhook_url']
        text = self._get_text()

        if not text:
            return

        result = None
        for chunk in self.chunkstring(text, self.MAX_LENGTH):
            res = self.submit_to_slack(webhook_url, chunk)
            if res.status_code != requests.codes.ok or res is None:
                result = res

        return result

    def _get_summary (self, line_length):
        return None

    def _format_details_item_title (self, title, type, line_length):
        suffix = ''
        if type == 'error':
            suffix = ':rotating_light: '
        elif type == 'new':
            suffix = ':leaves: '

        return '*%s%s*' % (suffix, title)


class CustomStdoutReporter(CustomReporter, reporters.StdoutReporter):

    __kind__ = 'custom-stdout'

    def submit(self):
        print = self._get_print()
        text = self._get_text()

        if not text:
            return

        print(self._get_text())

    def _format_summary (self, titles, line_length):
        summary = super()._format_summary(titles, line_length)
        summary = self._blue(summary)
        return summary

    def _format_summary_item (self, title, type, line_length):
        title = super()._format_summary_item(title, type, line_length)
        if type == 'error':
            title = self._red(title)
        elif type == 'new':
            title = self._green(title)
        else:
            title = self._blue(title)
        return title

    def _format_details_item_title (self, title, type, line_length):
        title = super()._format_details_item_title(title, type, line_length)
        if type == 'error':
            title = self._red(title)
        elif type == 'new':
            title = self._green(title)
        else:
            title = self._blue(title)
        return title
