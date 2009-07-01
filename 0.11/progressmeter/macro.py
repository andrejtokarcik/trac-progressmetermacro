# -*- coding: utf-8 -*-

import os

from trac.config import ExtensionOption
from trac.core import *
from trac.ticket.query import Query
from trac.ticket.roadmap import ITicketGroupStatsProvider, apply_ticket_permissions, \
                                get_ticket_stats
from trac.web.chrome import Chrome, ITemplateProvider, add_stylesheet
from trac.wiki.api import IWikiMacroProvider, parse_args
from trac.wiki.macros import WikiMacroBase

def query_stats_data(req, stat, constraints, grouped_by='component',
                     group=None):
    def query_href(extra_args):
        args = {grouped_by: group, 'group': 'status'}
        args.update(constraints)
        args.update(extra_args)
        return req.href.query(args)
    return {'stats': stat,
            'stats_href': query_href(stat.qry_args),
            'interval_hrefs': [query_href(interval['qry_args'])
                            for interval in stat.intervals]}

class ProgressMeterMacro(WikiMacroBase):
    """Progress meter (wiki macro) plugin for Trac

    Usage and installation instructions are available at:
        http://trac-hacks.org/wiki/ProgressMeterMacro
    """
    implements(IWikiMacroProvider, ITemplateProvider)

    stats_provider = ExtensionOption('progressmeter', 'stats_provider',
                                     ITicketGroupStatsProvider,
                                     'DefaultTicketGroupStatsProvider',
        """Name of the component implementing `ITicketGroupStatsProvider`,
        which is used to collect statistics on groups of tickets
        for meters generated by the ProgressMeterMacro plugin.""")

    ## IWikiMacroProvider methods
    def expand_macro(self, formatter, name, content):
        req = formatter.req

        # Parse arguments
        args, kwargs = parse_args(content, strict=False)
        kwargs.pop('status', None)  # ignore the `status' argument

        # Create & execute the query string
        qstr = '&'.join(['%s=%s' % item
                                for item in kwargs.iteritems()])
        query = Query.from_string(self.env, qstr, max=0)

        # Calculate stats
        qres = query.execute(req)
        tickets = apply_ticket_permissions(self.env, req, qres)

        stats = get_ticket_stats(self.stats_provider, tickets)
        stats_data = query_stats_data(req, stats, query.constraints)

        # ... and finally display them
        add_stylesheet(req, 'common/css/roadmap.css')
        return Chrome(self.env).render_template(req, 'progressmeter.html',
                                                stats_data)

    ## ITemplateProvider methods
    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        from pkg_resources import resource_filename
        return [resource_filename(__name__, 'templates')]
