# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke, hendrik.bunke@ifw-kiel.de

# provides statistics of economics papers

#TODO citations unterschieden nach dp und ja


#python imports
from sets import Set
import operator
import locale

# Zope imports 
from zope.interface import Interface

# CMF imports
from Products.CMFCore.utils import getToolByName

# Five imports
from Products.Five.browser import BrowserView

from Products.AdvancedQuery import Eq, And, Or, Ge, Le

from iqpp.rating.interfaces import IRatingsManager
from iqpp.clickcounting.interfaces import IClickCounting

from Products.eJournal.interfaces import ICitec


class IStatView(Interface):
    """
    """
    def comments():
        """count total number of portal comments
        """

    def countDP():
        """counts all discussionpapers
        """

    def countJP():
        """counts all journalpapers
        """

    def downloadsJP():
        """counts downloads of all Journalpapers
        """

    def downloadsDP():
        """counts downloads of all Discussionpapers
        """

    def averageJP():
        """calculates average downloads of JournalPapers
        """

    def averageDP():
        """calculates average downloads of Discussionpapers
        """

    def downloadsSUM():
        """sums downloads of all papers
        """

    def averageSUM():
        """average of all papers
        """

    def countReaders():
        """number of registered readers
        """

    def countRecommended():
        """number of recommendations and articles recommended
        """

    def countRatings():
        """counts number of ratings overall and articles that have been rated
        """

    def countAuthors():
        """counts number of authors
        """

    def countAssociateEditors():
        """counts number of AEs
        """

    def downloadsJPDP():
        """counts downloads of Journalpapers incl. their corresponding
        DiscussionPapers
        """

    def averageJPDP():
        """calculates average Downloads of Journalarticles incl. their
        correspondig Discussionpapers
        """

    def countCitations():
        """sums all Citec Citations
        """

    def topCitations():
        """gets the most cited papers
        """

    def countCitedDP():
        """counts all cited Discussionpapers
        """

    def countCitedJP():
        """counts all cited Journalarticles
        """

    def recentCitation():
        """
        returns the most recent paper with citations
        """

    def getRatedComments():
        """
        returns all comments with ratings
        """

    def getCommentRating():
        """returns rating of comment
        """

    def countCommentRating():
        """counts number of ratings for each comment
        """



class StatView(BrowserView):
    """provides statistics
    """
    
    def __formatNumber(self, number):
        """method for getting thousands separator on results
        """
        locale.setlocale(locale.LC_NUMERIC, 'de_DE.UTF-8')
        if type(number) == str:
            result = int(number.replace('.', ''))
        if type(number) == int:
            result = locale.format("%d", number, True)
        
        return result


    
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

       
    def downloadsJP(self):
        """counts downloads of all JournalPapers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(portal_type = "JournalPaper")
        amount = 0

        for brain in brains:
            obj = brain.getObject()
            for version in obj.objectValues("eJFile"):
                cc = IClickCounting(version)
                downloads = cc.getClicks()
                amount += downloads

        return self.__formatNumber(amount)

 
    def downloadsDP(self):
        """counts downloads of all DiscussionPapers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(portal_type = "DiscussionPaper")
        amount = 0

        for brain in brains:
            obj = brain.getObject()
            cc = IClickCounting(obj)
            downloads = cc.getClicks()
            amount +=downloads

        return self.__formatNumber(amount)


    def averageJP(self):
        """calculates average Download of Journalpapers
        """
        jp = self.countJP()
        downloads = self.__formatNumber(self.downloadsJP())
        #import pdb; pdb.set_trace()
        average = downloads / jp
        
        return average


    def averageDP(self):
        """calculates average download of Discussionpapers
        """
        dp = self.countDP()
        downloads = self.__formatNumber(self.downloadsDP())
        average = downloads / dp

        return average

    
    def downloadsSUM(self):
        """sums downloads of all papers
        """
        summe = self.__formatNumber(self.downloadsJP()) + self.__formatNumber(self.downloadsDP())
        return self.__formatNumber(summe)


    def averageSUM(self):
        """average download of all papers
        """
        
        downloads = self.__formatNumber(self.downloadsSUM())
        p = self.countJP() + self.countDP()
        average = downloads / p

        return average
        
    
    def countReaders(self):
        """number of registered readers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        query = And(Eq("portal_type", "eJMember"),
                    Or(Eq("review_state", "public"), Eq("review_state", "private"))
                    )
               
        brains = catalog.evalAdvancedQuery(query,)
        #brains = catalog.searchResults(portal_type = "eJMember")
        
        result = len(brains)
        return self.__formatNumber(result)

    def countRecommended(self):
        """counts articles with recommendations
        """
        catalog = getToolByName(self.context, "portal_catalog")
        query = Or(Eq("portal_type", "JournalPaper"),
                   Eq("portal_type", "DiscussionPaper"))
        brains = catalog.evalAdvancedQuery(query,)

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
        result = "%s Articles recommended by %s users (%s recommendations overall)" % (a, users, recommendations)
        return result

    def countRatings(self):
        """get amount of ratings and articles with ratings
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(portal_type = "JournalPaper")

        articles = []
        ratings = 0
        user = []

        for brain in brains:
            obj = brain.getObject()
            objID = obj.getId()
            rm = IRatingsManager(obj)
            rating = rm.computeAverage(id = 'score')
            amount_ratings = rm.countAmountRatings(id = 'score')
            rating_liste = rm.getRatings(id = 'score')
            if rating > 0:
                articles.append(obj)
                ratings += amount_ratings
                for entry in rating_liste:
                    
                    #die loesung aus countRecommendations mit Set() funktioniert hier nicht. 
                    # Frage ist, was effizienter ist
                    if entry.user not in user:
                        user.append(entry.user)
           

        a = len(articles)
        users = len(user)
        result = "%s Articles rated by %s users (%s ratings overall)" % (a, users, ratings)
        
        return result
                
        
    def countAuthors(self):
        """counts authors
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(portal_type = "Author")
        result = len(brains)
        
        
        return result

    def countAssociateEditors(self):
        """counts associated editors
        """

    def downloadsJPDP(self):
        """counts downloads of Journalarticles incl. their corresponding
        Discussionpapers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog.searchResults(portal_type = "JournalPaper")
        amount = 0

        for brain in brains:
            obj = brain.getObject()
            for version in obj.objectValues("eJFile"):
                cc = IClickCounting(version)
                downloads = cc.getClicks()
                amount += downloads
            
            if len(obj.getRefs('journalpaper_discussionpaper')) > 0:
                dp = obj.getRefs('journalpaper_discussionpaper')[0]
                cb = IClickCounting(dp)
                downloadsDP = cb.getClicks()
                amount += downloadsDP

        return self.__formatNumber(amount)
    

    def averageJPDP(self):
        """calculates average Downloads of Journalarticles incl. their
        correspondig Discussionpapers
        """
        jp = self.countJP()
        downloads = self.__formatNumber(self.downloadsJPDP())
        average = downloads / jp

        return self.__formatNumber(average)


    def countCitations(self):
        """count all citec citations
        """
        return self.countCitedDP() + self.countCitedJP()

    
    def maxCitations(self):
        """return list with most cited papers
        """
        catalog = getToolByName(self.context, "portal_catalog")
        query = Or(Eq('portal_type', 'DiscussionPaper'), 
                   Eq('portal_type', 'JournalPaper'))

        brains = catalog.evalAdvancedQuery(query)

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
        catalog = getToolByName(self.context, "portal_catalog")
        query = Or(Eq('portal_type', 'DiscussionPaper'), 
                   Eq('portal_type', 'JournalPaper'))

        brains = catalog.evalAdvancedQuery(query, (('created', 'desc'),))
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

    
    def getRatedComments(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog")
        query = And(Eq('portal_type', "Comment"), Ge('rating_helpful', 0))
        brains = catalog.evalAdvancedQuery(query, (("rating_helpful", "desc"),))
        
        return  [brain.getObject() for brain in brains]


    def getCommentRating(self):
        """
        """
        rm = IRatingsManager(self.context)
        rating = rm.computeAverage(id = 'helpful')
        return rating

    def countCommentRating(self):
        """
        """
        rm = IRatingsManager(self.context)
        cr = rm.countAmountRatings(id='helpful')
        return cr











            










