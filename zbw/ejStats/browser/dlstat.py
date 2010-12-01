from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.annotation.interfaces import IAnnotations
from plone.memoize.view import memoize

# FOR LATER USE
#from reportlab.graphics.shapes import Drawing
#from reportlab.graphics.charts.linecharts import HorizontalLineChart
#from reportlab.graphics.widgets.markers import uSymbol2Symbol, isSymbol, makeMarker

from Products.CMFCore.utils import getToolByName
from iqpp.clickcounting.interfaces import IClickCounting

from zbw.ejStats.utils import format_number


class DownloadStatistic(BrowserView):
    """
    """
    __call__ = ViewPageTemplateFile('dlstat.pt')
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.statsview = getMultiAdapter((self.context, self.context.request),
                name="stats")


    @memoize
    def __dl_over_time(self):
        """
        get a sorted dictionary with month as key
        """
        clickdates_view = getMultiAdapter((self.context, self.context.request),
                name='clickdates')
        objects = clickdates_view._getClickdatesObjects()

        dl_gesamt = {}
        
        for item in objects:
            ann = IAnnotations(item)
            dates = ann['hbxt.clickdates']
            for key in dates.keys():
                dlmonth = len(dates[key])
                if dl_gesamt.has_key(key):
                    dl_gesamt[key] = dl_gesamt[key] + dlmonth
                else:
                    dl_gesamt[key] = dlmonth

        #we have to rewrite the keys here because datetime stores month 1-9
        #without leading zero, which is needed for sorting
        dl_sorted = {}
        for key in dl_gesamt.iterkeys():
            ym = key.rsplit('-')
            if int(ym[1]) in range(1,10):
                month = ym[1].zfill(2)
                new_key = '%s-%s' % (ym[0], month)
            else:
                new_key = key
            dl_sorted[new_key] = dl_gesamt[key]
        
        #XXX this is only for ejournal use! remove may 2009 since we have not
        #data for the whole month
        del dl_sorted['2009-05']

        return dl_sorted
       
                
    def dl_listed(self):
        """
        """
        dl_sorted = self.__dl_over_time()
        dl_listed = []
        months = sorted(dl_sorted.iterkeys(),reverse=True)
        for month in months:
            tup = (month, dl_sorted[month])
            dl_listed.append(tup)
        
        return dl_listed

    def dl_minmax(self):
        """
        """
        dl_sorted = self.__dl_over_time()
        dlvalues = dl_sorted.values()
        dlvalues = sorted(dlvalues)
        dl_min = dlvalues[0]
        dl_max = dlvalues[-1]
        #import pdb; pdb.set_trace()
        return (dl_min, dl_max)



   #def dl_chart(self):
   #    """
   #    """
   #    drawing = Drawing(200, 100)

   #    data = [ 
   #            (13, 5, 20, 22, 37, 45, 19, 4), 
   #            (14, 10, 21, 28, 38, 46, 25, 5)
   #            ]   

   #    lc = HorizontalLineChart()

   #    lc.x = 20
   #    lc.y = 10
   #    lc.height = 85
   #    lc.width = 170 
   #    lc.data = data
   #    lc.lines.symbol = makeMarker('Circle')

   #    drawing.add(lc)
   #        
   #    drawing.save(fnRoot='test', formats=['png'])
   #    #return drawing

    @memoize    
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

        return format_number(amount)

    @memoize
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

        return format_number(amount)


    @memoize
    def averageJP(self):
        """calculates average Download of Journalpapers
        """
        jp = self.statsview.countJP()
        downloads = format_number(self.downloadsJP())
        #import pdb; pdb.set_trace()
        average = downloads / jp
        
        return average

    @memoize
    def averageDP(self):
        """calculates average download of Discussionpapers
        """
        dp = self.statsview.countDP()
        downloads = format_number(self.downloadsDP())
        average = downloads / dp

        return average

    
    def downloadsSUM(self):
        """sums downloads of all papers
        """
        summe = format_number(self.downloadsJP()) + format_number(self.downloadsDP())
        return format_number(summe)


    def averageSUM(self):
        """average download of all papers
        """
        
        downloads = format_number(self.downloadsSUM())
        p = self.statsview.countJP() + self.statsview.countDP()
        average = downloads / p

        return average
    
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

        return format_number(amount)
 
    def averageJPDP(self):
        """calculates average Downloads of Journalarticles incl. their
        correspondig Discussionpapers
        """
        jp = self.statsview.countJP()
        downloads = format_number(self.downloadsJPDP())
        average = downloads / jp

        return format_number(average)

