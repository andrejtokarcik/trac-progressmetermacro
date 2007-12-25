# -*- coding: utf-8 -*-

"""
ProgressMeter (wiki macro) plugin
Usage and installation instructions can be found at:
    http://trac-hacks.org/wiki/ProgressMeterMacro
"""


from genshi.builder import tag

from trac.core import *
from trac.wiki.api import IWikiMacroProvider
from trac.wiki.macros import WikiMacroBase
from trac.ticket.query import Query

class MacroSyntaxError(Exception):
    """Exception raised when a macro gets not valid arguments."""

class ProgressMeterMacro(WikiMacroBase):
    implements(IWikiMacroProvider)

    # IWikiMacroProvider methods
    def expand_macro(self, formatter, name, content):
        # Testing if passed arguments are correct
        if type(content) != unicode or len(content) == 0:
            raise MacroSyntaxError, 'ProgressMeter macro requires at least one argument'

        # Transforming arguments passed to macro into a list and stripping them
        content = [v.strip() for v in content.split(',')]

        # Testing if passed arguments have correct form
        for value in content:
            if value.find('=') == -1:
                raise MacroSyntaxError, 'ProgressMeter macro requires field and ' \
                                        'constraints separated by a "="'

        # Setting query strings for closed and active tickets
        query_strings = []
        query_strings.append('&'.join(['%s' % item
                                 for item in content]))   # active tickets
        content.append('status=closed')
        query_strings.append('&'.join(['%s' % item
                                 for item in content]))   # closed tickets

        # Getting exact numbers of tickets that match query strings
        i = 0; query = []; tickets = []; cnt = []
        for query_string in query_strings:
            query.append(Query.from_string(self.env, query_string))
            tickets.append(query[i].execute(formatter.req))
            cnt.append(tickets[i] and len(tickets[i]) or 0)
            i = i + 1

        # Getting percent of active/closed tickets + formatting output
        percents = {}
        # tuple of percent and style for each type of tickets (closed, active)
        percents['closed'] = [float(cnt[1]) / float(cnt[0]), 'background: #bae0ba']
        percents['active'] = [1 - percents['closed'][0], 'background: #f5f5f5']

        # CSS styles are mostly copied from htdocs/css/rodamap.css
        # in standard trac distribution
        table_css = '''
             border: 1px solid #d7d7d7;
             border-collapse: collapse;
             border-spacing: 0;
             float: left;
             margin: 3px 4px 3px 0;
             empty-cells: show;
             height: 1.2em;
             width: 40em;
        '''

        table = tag.table(style=table_css)(tag.tr())
        for key in reversed(percents.keys()):
            percents[key][0] = unicode(int(percents[key][0] * 100)) + u'%'
            table.children[0](tag.td(style='width: '+percents[key][0]+'; '+percents[key][1]+'; padding: 0')(''))

        percent_para = tag.p(style='font-size: 10px; line-height: 2.4em')(percents['closed'][0])

        output = table + percent_para
        # Returning...
        return output 
