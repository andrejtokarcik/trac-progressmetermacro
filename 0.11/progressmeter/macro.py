# -*- coding: utf-8 -*-
"""
Progress meter macro plugin for Trac.
"""

from genshi.builder import tag

from trac.core import *
from trac.wiki.api import IWikiMacroProvider, parse_args
from trac.web.chrome import add_stylesheet, ITemplateProvider
from trac.wiki.macros import WikiMacroBase
from trac.ticket.query import Query, QueryModule


__all__ = ['ProgressMeterMacro']

class ProgressMeterMacro(WikiMacroBase):
    """
    ProgressMeter (wiki macro) plugin
    Usage and installation instructions can be found at:
        http://trac-hacks.org/wiki/ProgressMeterMacro
    """
    implements(IWikiMacroProvider, ITemplateProvider)

    ## IWikiMacroProvider methods
    def expand_macro(self, formatter, name, content):
        # Parsing arguments (copied from ticket/query.py from standard trac distribution)
        # suggested by dhellmann
        args, kwargs = parse_args(content, strict=False)

        # get statuses which will be used in the query strings
        statuses = kwargs.pop('status', 'closed').split('|')

        # Create query strings for some ticket statuses
        _qstr = '&'.join(['%s=%s' % item
                                 for item in kwargs.iteritems()])

        query_string = dict()
        query_string['total'] = _qstr

        types = {'active': '!%s', 'closed': '%s'}
        for t in types:
            query_string[t] = '&'.join([query_string['total'], 'status=' +
              '|'.join([types[t] % status for status in statuses])])

        # Execute queries
        cnt = dict()
        for key in ('closed', 'total'):
            query = Query.from_string(self.env, query_string[key])
            tickets = query.execute(formatter.req)
            cnt[key] = (tickets and len(tickets) or 0)

        # calculate the number of active tickets
        cnt['active'] = cnt['total'] - cnt['closed']

        # Getting percent of active/closed tickets
        try:
            percents = {'closed': float(cnt['closed']) / float(cnt['total'])}
        except ZeroDivisionError:
            raise Exception('No tickets found for provided constraints')
        percents['active'] = 1 - percents['closed']

        # Start displaying
        add_stylesheet(formatter.req, 'progressmeter/css/progressmeter.css')
        main_div = tag.div(class_='milestone')

        # add title above progress bar
        args and main_div.children.append(tag.h2(args))

        # add progress bar
        table = tag.table(class_='progress')(tag.tr())

        # create links
        links = dict()
        for key in query_string:
            # Trac QueryModule doesn't know how to handle status=x|y (what
            # is used in the query strings) so transforming to
            # status=x&status=y (what will be used in hyperlinks)
            links[key] = query_string[key].replace('|', '&status=')

        for key in reversed(percents.keys()):
            # reversing because we want the closed tickets to be processed firstly
            percents[key] = unicode(int(percents[key] * 100)) + u'%'
            table.children[0](tag.td(style='width: '+percents[key], class_=key)
              (tag.a(title="%i of %i tickets %s" % (cnt[key], cnt['total'], key.title()),
              href="%s?%s" % (formatter.href.query(), links[key]))))
        main_div.children.append(table)

        # add percentage displaied to the right of the progress bar
        percent_para = tag.p(class_='percent')(percents['closed'])
        main_div.children.append(percent_para)

        # add ticket count below progress bar
        ticket_count = tag.dl()

        for key in links.keys():
            ticket_count.children.append(tag.dt()("%s tickets:" % key.title()))
            ticket_count.children.append(tag.dd()(tag.a(str(cnt[key]),
              href="%s?%s" % (formatter.href.query(), links[key]))))
        main_div.children.append(ticket_count)

        return main_div


    ## ITemplateProvider methods
    def get_htdocs_dirs(self):
        """Makes the 'htdocs' folder available for Trac."""
        from pkg_resources import resource_filename
        return [('progressmeter', resource_filename('progressmeter', 'htdocs'))]

    def get_templates_dirs(self):
        return []  # must return an iterable

