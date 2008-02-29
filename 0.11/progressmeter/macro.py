# -*- coding: utf-8 -*-
"""
ProgressMeterMacro plugin for Trac.

License: GPLv2

Author: Andrej Tokarčík
Thanks to: Doug Hellman, osimons
"""

from genshi.builder import tag

from trac.core import *
from trac.wiki.api import IWikiMacroProvider, parse_args
from trac.web.chrome import add_stylesheet, ITemplateProvider
from trac.wiki.macros import WikiMacroBase
from trac.ticket.query import Query


__all__ = ['ProgressMeterMacro']

class ProgressMeterMacro(WikiMacroBase):
    """
    ProgressMeter (wiki macro) plugin
    Usage and installation instructions can be found at:
        http://trac-hacks.org/wiki/ProgressMeterMacro
    """
    implements(IWikiMacroProvider, ITemplateProvider)

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
            # first cycle -- getting number of all tickets matching the criteria (cnt[0])
            # second cycle -- getting number of closed tickets matching the criteria (cnt[1])
            query_string = '&'.join(['%s=%s' % item
                                 for item in kwargs.iteritems()]) + qs_add[i]
            query = Query.from_string(self.env, query_string)
            tickets = query.execute(req)
            cnt.append(tickets and len(tickets) or 0)

        # Getting percent of active/closed tickets + formatting output
        percents = {}
        # list of percent and CSS class for each type of tickets (closed, active)
        percents['closed'] = [float(cnt[1]) / float(cnt[0]), 'closed']
        percents['active'] = [1 - percents['closed'][0], 'active']

        # Formatting output...
        # (separate css is made using some parts of osimons's fullblog plugin)
        add_stylesheet(formatter.req, 'progressmeter/css/progressmeter.css')

        main_div = tag.div(class_='progressmeter')
        table = tag.table()(tag.tr())

        for key in reversed(percents.keys()):
            # reversing because we want the closed tickets to be processed firstly
            percents[key][0] = unicode(int(percents[key][0] * 100)) + u'%'
            table.children[0](tag.td(style='width: '+percents[key][0]+'', class_=percents[key][1])(''))

        percent_para = tag.p()(percents['closed'][0])

        main_div.children = [table, percent_para]
        return main_div  # Returning...


    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """ Makes the 'htdocs' folder inside the egg available. """
        from pkg_resources import resource_filename
        return [('progressmeter', resource_filename('progressmeter', 'htdocs'))]

    def get_templates_dirs(self):
        return []  # must return an iterable

