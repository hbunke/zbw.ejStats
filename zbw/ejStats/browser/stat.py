# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke, hendrik.bunke@ifw-kiel.de
# provides statistics of economics papers

from operator import itemgetter
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zbw.ejCitations.interfaces import ICitec
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zbw.ejStats.utils import format_number
from zbw.ejStats.browser.interfaces import IStatView
from plone.memoize.view import memoize


class StatView(BrowserView):
    """
    provides statistics
    """
    implements(IStatView)
    template = ViewPageTemplateFile('stat.pt')

    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()

    def get_brains(self, pt, **kwargs):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type=pt, **kwargs)
    
    def count_pt(self, pt):
        return len(self.get_brains(pt))

    def count_cited_pt(self, pt):
        return sum(map(count_citations, self.get_brains(pt)))

    @memoize
    def get_all_cited_papers(self):
        brains = self.get_brains(('JournalPaper', 'DiscussionPaper'))
        return [(brain.getObject(), count_citations(brain)) for brain in brains
                if count_citations(brain) > 0]

    def countReaders(self):
        """number of registered readers
        """
        brains = self.get_brains("eJMember", review_state=("public", "private"))
        result = len(brains)
        return format_number(result)
    
    def maxCitations(self):
        """return most cited papers
        """
        cited_papers = self.get_all_cited_papers()
        return sorted(cited_papers, key=itemgetter(1), reverse=True)

    def recentCitation(self):
        """return most recently published paper with citations
        """
        cited_papers = self.get_all_cited_papers()
        fn = lambda t: (t[0], t[1], t[0].created())
        ncp = map(fn, cited_papers)
        maxi = lambda a, b: max(a, b, key=itemgetter(2))
        return [reduce(maxi, ncp)]  # don't know why template wants list here


def count_citations(brain):
    obj = brain.getObject()
    citec = ICitec(obj)
    return citec.count_citations()

