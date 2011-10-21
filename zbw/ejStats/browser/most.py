# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.interface import Interface
#from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from iqpp.clickcounting.interfaces import IClickCounting

class Downloaded(BrowserView):
    """
    lists the most downloaded journalarticles;
    should be obsolete since we have a 'sort by downloads' in standard listing
    of journalarticles
    """

    template = ViewPageTemplateFile("most_downloaded.pt")
    
    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()

    def get_most_downloaded_JP(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(portal_type="JournalPaper", review_state="published", 
                sort_on="amount_downloads", sort_order="descending")

        result = []
        for brain in brains:
            obj = brain.getObject()
            if IClickCounting(obj).getClicks() > 0:  
                result.append(obj) 
        return result


class Commented(BrowserView):
    """
    lists most commented papers
    """
    template = ViewPageTemplateFile('most_commented.pt')

    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()

    
    def get_most_commented(self):
        """
        """
        catalog = getToolByName(self.context, "portal_catalog")
        brains = catalog(
                   portal_type=("DiscussionPaper", "JournalPaper"), 
                   sort_on="amount_comments", 
                   sort_order="descending")

        papers = [brain.getObject() for brain in brains[:50]]
        result = []
        for paper in papers:
            brains = catalog(
                    path = "/".join(paper.getPhysicalPath()),
                    portal_type = "Comment"
                    )
        
            paper.comments = len(brains)
            result.append((paper, paper.comments))

        return result





