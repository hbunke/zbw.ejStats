# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke, hendrik.bunke@ifw-kiel.de

# provides statistics of economics papers

#TODO citations unterschieden nach dp und ja


from sets import Set
import operator

from zope.interface import implements

from Products.CMFCore.utils import getToolByName

from Products.Five.browser import BrowserView

from Products.AdvancedQuery import Eq, And, Or

from zbw.ejCitations.interfaces import ICitec
from zbw.ejCrossref.interfaces import ICrossrefCitations, ICrossrefItem
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zbw.ejStats.utils import format_number
from zbw.ejStats.browser.interfaces import IStatView
from plone.memoize.view import memoize


class StatView(BrowserView):
    """provides statistics
    """
    implements(IStatView)

    __call__ = ViewPageTemplateFile('stat.pt')
   
    
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
         
        brains = catalog.searchResults(portal_type = "Comment")

        amount = len(brains)
        return amount
        

    def countDP(self):
        """number of discussion papers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(portal_type = "DiscussionPaper")
        result = len(brains)
        return result

    
    def countJP(self):
        """number of journal papers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(portal_type = "JournalPaper")
        result = len(brains)
        return result
       
    
    def countReaders(self):
        """number of registered readers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        query = And(Eq("portal_type", "eJMember"),
                    Or(Eq("review_state", "public"), 
                        Eq("review_state", "private"))
                    )
               
        brains = catalog.evalAdvancedQuery(query,)
        #brains = catalog.searchResults(portal_type = "eJMember")
        
        result = len(brains)
        return format_number(result)

    def countRecommended(self):
        """counts articles with recommendations
        """
        brains = self.get_all_papers()

        articles = []
        recommendations = 0
        user = []

        for brain in brains:
            obj = brain.getObject()
            rc_by = obj.getRecommended_by()
            if len(rc_by) > 0:
                articles.append(obj)
                recommendations += len(rc_by)
                user.append(rc_by)

        a = len(articles)
        users = len(Set(user))
        result = "%s Articles recommended by %s users \
                (%s recommendations overall)" % (a, users, recommendations)
        return result

        
    def countAuthors(self):
        """counts authors
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(portal_type = "Author")
        result = len(brains)
        
        
        return result

       

    def countCitations(self):
        """count all citec citations
        """
        return self.countCitedDP() + self.countCitedJP()

    
    def maxCitations(self):
        """return list with most cited papers
        """
        brains = self.get_all_papers()

        citedPapers = []

        for brain in brains:
            obj = brain.getObject()
            citec = ICitec(obj)
            if citec.hasHandle():
                rss = citec.getCitecRSS()
                count = len(rss['entries'])
                if count > 0:
                    citedPapers.append((obj, count))

        mostCitedPapers = sorted(citedPapers, key=operator.itemgetter(1))
        mostCitedPapers.reverse()
        return mostCitedPapers


    def countCitedDP(self):
        """return number of counted discussionpapers
        """
        catalog = getToolByName(self.context, "portal_catalog")

        brains = catalog(portal_type="DiscussionPaper")
        
        citations = 0
       
        for brain in brains:
            obj = brain.getObject()
            citec = ICitec(obj)
            if citec.hasHandle():
                rss = citec.getCitecRSS()
                count = len(rss['entries'])
                if count > 0:
                    citations += count

        return citations

    def countCitedJP(self):
        """return number of counted journalarticles
        """
        catalog = getToolByName(self.context, "portal_catalog")

        brains = catalog(portal_type="JournalPaper")
        
        citations = 0
       
        for brain in brains:
            obj = brain.getObject()
            citec = ICitec(obj)
            if citec.hasHandle():
                rss = citec.getCitecRSS()
                count = len(rss['entries'])
                if count > 0:
                    citations += count

        return citations

    
    def recentCitation(self):
        """
        """
        brains = self.get_all_papers()
        citedPapers = []

        for brain in brains:
            obj = brain.getObject()
            citec = ICitec(obj)
            if citec.hasHandle():
                rss = citec.getCitecRSS()
                count = len(rss['entries'])
                if count > 0:
                    citedPapers.append((obj, count))
        return citedPapers[:1]


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

