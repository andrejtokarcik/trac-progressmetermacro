# -*- coding: utf-8 -*-

# For information about author, license, etc. see setup.py

from genshi.builder import tag

from trac.core import *
from trac.wiki.api import IWikiMacroProvider
from trac.wiki.macros import WikiMacroBase
from trac.ticket.query import Query
from trac.wiki.api import parse_args


__all__ = ['ProgressMeterMacro']

class ProgressMeterMacro(WikiMacroBase):
    """
    ProgressMeter (wiki macro) plugin
    Usage and installation instructions can be found at:
        http://trac-hacks.org/wiki/ProgressMeterMacro
    """
    implements(IWikiMacroProvider)

    # IWikiMacroProvider methods
    def expand_macro(self, formatter, name, content):
        # Stripping content -- allows using spaces within arguments --
        # and checking whether there is not argument 'status'
        content = ','.join([x.strip() for x in content.split(',') if not x.strip().startswith('status')])

        # Parsing arguments (copied from ticket/query.py from standard trac distribution)
        # suggested by dhellman
        req = formatter.req
        query_string = ''
        argv, kwargs = parse_args(content, strict=False)
        if len(argv) > 0 and not 'ticket_value' in kwargs: # 0.10 compatibility hack
            kwargs['ticket_value'] = argv[0]

        ticket_value = kwargs.pop('ticket_value', 'list').strip().lower()
        query_string = '&'.join(['%s=%s' % item
                                 for item in kwargs.iteritems()])

        cnt = []; qs_add = ['', '&status=closed']
        for i in [0, 1]:
            query_string = '&'.join(['%s=%s' % item
                                 for item in kwargs.iteritems()]) + qs_add[i]
            query = Query.from_string(self.env, query_string)
            tickets = query.execute(req)
            cnt.append(tickets and len(tickets) or 0)

        # Getting percent of active/closed tickets + formatting output
        percents = {}
        # list of percent and style for each type of tickets (closed, active)
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
            # reversing because we want the closed tickets to be first
            percents[key][0] = unicode(int(percents[key][0] * 100)) + u'%'
            table.children[0](tag.td(style='width: '+percents[key][0]+'; '+percents[key][1]+'; padding: 0')(''))

        percent_para = tag.p(style='font-size: 10px; line-height: 2.4em')(percents['closed'][0])

        output = table + percent_para
        # Returning...
        return output 
