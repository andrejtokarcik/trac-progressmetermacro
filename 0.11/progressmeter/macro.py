# -*- coding: utf-8 -*-
"""
Progress meter macro plugin for Trac.
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
        query_string = '&'.join(['%s=%s' % item for item in kwargs.iteritems()])
        cnt = {}
        qs_add = {'total': '', 'closed': '&status=closed', 'active': '&status=!closed'}
        for key in ('closed', 'total'):
            query = Query.from_string(self.env, query_string + qs_add[key])
            tickets = query.execute(req)
            cnt[key] = (tickets and len(tickets) or 0)

        # calculate the number of active tickets
        cnt['active'] = cnt['total'] - cnt['closed']

        # Getting percent of active/closed tickets
        percents = {'closed': float(cnt['closed']) / float(cnt['total'])}
        percents['active'] = 1 - percents['closed']

        add_stylesheet(formatter.req, 'progressmeter/css/progressmeter.css')

        main_div = tag.div(class_='milestone')

        # Add title above progress bar
        argv and main_div.children.append(tag.h2(argv))

        # Add progress bar
        table = tag.table(class_='progress')(tag.tr())

        for key in reversed(percents.keys()):
            # reversing because we want the closed tickets to be processed firstly
            percents[key] = unicode(int(percents[key] * 100)) + u'%'
            table.children[0](tag.td(style='width: '+percents[key], class_=key)
              (tag.a(title="%i of %i tickets %s" % (cnt[key], cnt['total'], key.title()),
              href="%s?%s" % (formatter.href.query(),query_string + qs_add[key]))))
        main_div.children.append(table)

        # Add percentage displaied to the right of the progress bar
        percent_para = tag.p(class_='percent')(percents['closed'])
        main_div.children.append(percent_para)

        # Add ticket count below progress bar
        ticket_count = tag.dl()

        for key in qs_add.keys():
            ticket_count.children.append(tag.dt()("%s tickets:" % key.title()))
            ticket_count.children.append(tag.dd()(tag.a(str(cnt[key]),
              href="%s?%s" % (formatter.href.query(), query_string + qs_add[key]))))
        main_div.children.append(ticket_count)

        return main_div


    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        """ Makes the 'htdocs' folder available for Trac. """
        from pkg_resources import resource_filename
        return [('progressmeter', resource_filename('progressmeter', 'htdocs'))]

    def get_templates_dirs(self):
        return []  # must return an iterable

