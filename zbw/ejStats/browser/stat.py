# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke, hendrik.bunke@ifw-kiel.de
# provides statistics of economics papers


from sets import Set
import operator
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

    
    @memoize
    def get_all_papers(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type=('JournalPaper', 'DiscussionPaper'), 
                sort_on="created", sort_order="descending")
        return brains


    def comments(self):
        """counts comments on discussion papers and journalarticles
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type = "Comment")
        return len(brains)
        

    def countDP(self):
        """number of discussion papers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type = "DiscussionPaper")
        return len(brains)

    
    def countJP(self):
        """number of journal papers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type = "JournalPaper")
        return len(brains)
       
    
    def countReaders(self):
        """number of registered readers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type="eJMember", 
                review_state=("public", "private"))
        
        result = len(brains)
        return format_number(result)

    
        
    def countAuthors(self):
        """counts authors
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type = "Author")
        return len(brains)


    def countCitations(self):
        """count all citec citations
        """
        return self.countCitedDP() + self.countCitedJP()

    
    def maxCitations(self):
        """return list with most cited papers
        """
        brains = self.get_all_papers()
        ot = ((brain.getObject(), count_citations(brain)) for brain in brains)
        cited_papers = filter(lambda b: b[1] > 0, ot)
        mostCitedPapers = sorted(cited_papers, key=operator.itemgetter(1),
                reverse=True)
        return mostCitedPapers


    def countCitedDP(self):
        """
        return number of counted discussionpapers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type="DiscussionPaper")
        cn = map(count_citations, brains)
        return sum(cn)

    
    def countCitedJP(self):
        """
        return number of counted journalarticles
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type="JournalPaper")
        cn = map(count_citations, brains)
        return sum(cn)

    def recentCitation(self):
        """
        """
        brains = self.get_all_papers()
        citedPapers = []

        for brain in brains:
            obj = brain.getObject()
            citec = ICitec(obj)
            count = citec.count_citations()
            if count > 0:
                citedPapers.append((obj, count))
        return citedPapers[:1]


def count_citations(brain):
    obj = brain.getObject()
    citec = ICitec(obj)
    return citec.count_citations()

