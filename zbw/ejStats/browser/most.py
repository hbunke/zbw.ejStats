# -*- coding: UTF-8 -*-

# Dr. Hendrik Bunke <h.bunke@zbw.eu>
# German National Library of Economics (ZBW)
# http://zbw.eu/

from DateTime import DateTime
from operator import itemgetter
from datetime import datetime
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from zope.interface import Interface
#from zope.component import getMultiAdapter
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName
from iqpp.clickcounting.interfaces import IClickCounting
from plone.memoize.view import memoize
from zbw.ejStats.utils import format_number


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


class DownloadedRange(BrowserView):
    """
    returns most downloaded papers in given date range
    """

    template = ViewPageTemplateFile("most_downloaded_range.pt")
    
    def __call__(self):
        self.request.set('disable_border', True)
        return self.template()
    
    def __init__(self, context, request):

        self.context = context
        self.request = request
    
    
    @memoize
    def downloads_in_range(self):
        """
        """
        
        try:
            date1 = self.request['date1']
            date2 = self.request['date2']
        except:
            return None
        
        #for now date format is html5 based yyyy-mm-dd. we have to convert it
        #to datetime
        date1 = self._convert(date1)
        date2 = self._convert(date2)

        
        catalog = getToolByName(self.context, "portal_catalog")
        
        #filter objects. papers created after date2 are not necessary
        start = DateTime(2007,1,1)
        end = self._convert(self.request['date2'],'zope')
        date_range_query = { 'query':(start,end), 'range': 'min:max'}
        
        
        pt = None
        try:
            pt = self.request['pt']
        
            if type(pt) == list:
                pt = tuple(pt)
            if type(pt) == str:
                pt = (pt,)
        except:
            pass
        

        brains = catalog(
                portal_type = pt,
                created = date_range_query
        )

        papers = [brain.getObject() for brain in brains]
        paper_list = []
        for paper in papers:
            ann = IAnnotations(paper)
            try:
                dates = ann['hbxt.clickdates']
            except:
                pass

            datetime_list = []
            drange = []
            #value is a PersistentList
            for value in dates.values():
                for date in value:
                    datetime_list.append(date)
            for dt in datetime_list:
                if dt > date1 and dt < date2:
                    drange.append(dt)
                    
            dl = len(drange)
            if dl > 0:
                paper_list.append({'article': paper, 'downloads': dl})
        
        #return paper_list
        return sorted(paper_list, key=itemgetter('downloads'), reverse=True)


    def dl_amount(self):
        """
        total number of downloads in given range and portal_type
        """
        papers = self.downloads_in_range()
        return format_number(sum(map(lambda p: p['downloads'], papers)))
        

    
    def pt_check(self):
        """
        """
        ja = 'checked'
        dp = 'checked'
        try:
            pt = self.request['pt']
            if not 'JournalPaper' in pt:
                ja = ''
            if not 'DiscussionPaper' in pt:
                dp = ''
        except:
            pass
        return {'ja': ja, 'dp': dp}
            



    def _convert(self, date, dt=''):
        """
        """
        datesplit = date.split('-')
        year = int(datesplit[0])
        month = int(datesplit[1])
        day = int(datesplit[2])
        
        if dt == 'zope':
            date = DateTime(year,month,day)
        else:
            date = datetime(year, month, day)
        
        return date

    





