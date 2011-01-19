from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.app.annotation.interfaces import IAnnotations
#from plone.memoize.view import memoize
from Products.CMFCore.utils import getToolByName
from zbw.ejCrossref.interfaces import ICrossrefCitations, ICrossrefItem


class CrossrefCitationsView(BrowserView):
    """
    which articles have been cited by whom?
    """
    __call__ = ViewPageTemplateFile('crossrefstat.pt')
    
   #def __init__(self, context, request):
   #    self.context = context
   #    self.request = request
   #    self.statsview = getMultiAdapter((self.context, self.context.request),
   #            name="stats")

    def count_crossref_citations(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog") 
        #interface marker abfrage abstrakter als nur journalarticle. 
        #I really love interfaces
        brains = catalog(object_provides=ICrossrefItem.__identifier__)
        #brains = catalog(portal_type="JournalPaper")
        citations = 0
        for brain in brains:
            obj = brain.getObject()
            crossref_citations = ICrossrefCitations(obj)
            nr_of_citations = crossref_citations.count_citations()
            if nr_of_citations:
                citations += nr_of_citations
        return citations

    def articles_with_citations(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog") 
        #interface marker abfrage abstrakter als nur journalarticle. 
        #I really love interfaces
        brains = catalog(object_provides=ICrossrefItem.__identifier__)
        cited_articles = []
        for brain in brains:
            obj = brain.getObject()
            crossref_citations = ICrossrefCitations(obj)
            nr_of_citations = crossref_citations.count_citations()
            if nr_of_citations > 0:
                cited_articles.append((obj, nr_of_citations))
        return cited_articles

    def cited_in(self):
        """
        """
        citations = ICrossrefCitations(self.context)
        if citations.has_citations():
            journals = citations.cited_in()
            return journals
        return None

