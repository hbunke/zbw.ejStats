from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.annotation.interfaces import IAnnotations
from plone.memoize.view import memoize
from Products.ATContentTypes.utils import DT2dt
import datetime
from operator import div, lt, eq, itemgetter


# FOR LATER USE
#from reportlab.graphics.shapes import Drawing
#from reportlab.graphics.charts.linecharts import HorizontalLineChart
#from reportlab.graphics.widgets.markers import uSymbol2Symbol, isSymbol, makeMarker

from Products.CMFCore.utils import getToolByName
from iqpp.clickcounting.interfaces import IClickCounting
from zbw.ejStats.utils import format_number

# we could use chain.from_iterable here, but toolz.concat is shorter (and uses
# chain.from_iterables)
#from itertools import chain
from toolz.itertoolz import concat
from toolz.functoolz import pipe
from toolz.dicttoolz import keymap


def clickcount(obj):
    cc = IClickCounting(obj)
    return cc.getClicks()


def average(papers, downloads):
  #  avg = lambda dl: {gt(dl, 0): div(dl, papers), eq(dl, 0): 0}.get(True)
    avg = lambda dl: {dl > 0: dl / papers, dl == 0: 0}.get(True)
    return avg(downloads)


def add_leading_zero(key):
    """
    add leading zero to month keys. needed for sorting
    """
    ym = key.rsplit('-')
    if int(ym[1]) in range(1, 10):
        month = ym[1].zfill(2)
        new_key = '{}-{}'.format(ym[0], month)
    else:
        new_key = key
    return new_key


class DownloadStatistic(BrowserView):
    """
    """
    template = ViewPageTemplateFile('dlstat.pt')
    
    def __call__(self):
        self.request.set('disable_border', True)
        self.statsview = getMultiAdapter((self.context, self.request),
                name="stats")

        if not self.request.has_key('days') or self.request['days'] == "":
            self.request.set('days', 30)

        return self.template()
    
    
    def get_brains(self, pt, **kwargs):
        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(portal_type=pt, **kwargs)
    
    def get_objects(self, pt):
        brains = self.get_brains(pt)
        return (brain.getObject() for brain in brains)

    @memoize
    def get_clickdates_objects(self):
        brains = self.get_brains(('JournalPaper', 'DiscussionPaper'),
            sort_on="created", sort_order="descending")
        objects = filter(lambda obj: 'hbxt.clickdates' in IAnnotations(obj),
                (brain.getObject() for brain in brains))
        
        return objects

    
    def __was_new(self, dates, created):
        """
        checks if article was recent when download occured
        """
        #days an article is considered to be new
        #delta = 30 
        delta = int(self.request['days'])

        #convert old Zope DateTime to python datetime
        obj_date = DT2dt(created).replace(tzinfo=None)
        
        d = datetime.timedelta(days=delta)
        
        counter = 0
        for clickdate in dates:
            e = clickdate - d
            if obj_date > e:
                counter += 1
        
        return counter

    @memoize
    def __dl_over_time(self):
        """
        get a sorted dictionary with month as key
        """
        annotations = lambda obj: IAnnotations(obj)['hbxt.clickdates']
        dates = map(annotations, self.get_clickdates_objects())
        keyse = concat(map(lambda date: map(lambda k: k, date.keys()), dates))
        dl_gesamt = {k: {'Sum': 0, 'new': 0, 'JournalPaper': 0,
            'DiscussionPaper': 0} for k in keyse}

        # XXX can we do this more functional?
        def update_dic(obj):
            d = dl_gesamt
            dates = annotations(obj)
            for key in dates.keys():
                count = len(dates[key])
                d[key]['Sum'] += count
                d[key][obj.portal_type] += count
                was_new = self.__was_new(dates[key], obj.created())
                d[key]['new'] += was_new
        
        map(update_dic, self.get_clickdates_objects())
        return keymap(add_leading_zero, dl_gesamt)
        
                
    def dl_listed(self):
        """
        """
        dl_sorted = self.__dl_over_time()
        months = sorted(dl_sorted.iterkeys(),reverse=True)
        return map(lambda m: (m, dl_sorted[m]), months)

    @memoize
    def downloads(self, pt):
        objects = self.get_objects(pt)
        ejfiles = lambda jp: concat(map(lambda obj: obj.objectValues("eJFile"), jp))
        dpfiles = lambda dp: dp
        files = {'JournalPaper': ejfiles, 'DiscussionPaper': dpfiles}.get(pt)
        return pipe(map(clickcount, files(objects)), sum, format_number)

    def average_downloads(self, pt):
        papers = self.statsview.count_pt(pt)
        downloads = self.downloads(pt)
        return average(papers, format_number(downloads))

    @memoize
    def downloadsSUM(self):
        """sums downloads of all papers
        """
        fn = format_number
        summe = fn(self.downloads('JournalPaper')) + fn(self.downloads('DiscussionPaper'))
        return fn(summe)

    def averageSUM(self):
        """average download of all papers
        """
        downloads = format_number(self.downloadsSUM())
        papers = self.statsview.count_pt('JournalPaper') + self.statsview.count_pt('DiscussionPaper')
        return average(papers, downloads)
    
    @memoize
    def downloadsJPDP(self):
        """counts downloads of Journalarticles incl. their corresponding
        Discussionpapers
        """
        objects = self.get_objects('JournalPaper')
        dl_jp = format_number(self.downloads('JournalPaper'))
        obj_filter = filter(lambda obj: obj.getRefs('journalpaper_discussionpaper'), objects)
        dps = (obj.getRefs('journalpaper_discussionpaper')[0] for obj in obj_filter)
        dl_dp = sum(map(clickcount, dps))
        return format_number(dl_jp + dl_dp)
 
    def averageJPDP(self):
        """calculates average Downloads of Journalarticles incl. their
        correspondig Discussionpapers
        """
        papers = self.statsview.count_pt('JournalPaper')
        downloads = format_number(self.downloadsJPDP())
        return average(papers, downloads)


    #def dl_minmax(self):
        #     """
        #     """
        #     dl_sorted = self.__dl_over_time()
        #     dlvalues = dl_sorted.values()
        #     dlvalues = sorted(dlvalues)
        #     dl_min = dlvalues[0]
        #     dl_max = dlvalues[-1]
        #     #import pdb; pdb.set_trace()
        #     return (dl_min, dl_max)



        # def dl_chart(self):
        #     """
        #     """
        #     drawing = Drawing(200, 100)

        #     data = [ 
        #             (13, 5, 20, 22, 37, 45, 19, 4), 
        #             (14, 10, 21, 28, 38, 46, 25, 5)
        #             ]   

        #     lc = HorizontalLineChart()

        #     lc.x = 20
        #     lc.y = 10
        #     lc.height = 85
        #     lc.width = 170 
        #     lc.data = data
        #     lc.lines.symbol = makeMarker('Circle')

        #     drawing.add(lc)
        #         
        #     drawing.save(fnRoot='test', formats=['png'])
        #     return drawing
        
