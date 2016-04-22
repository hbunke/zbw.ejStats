from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.annotation.interfaces import IAnnotations
from plone.memoize.view import memoize
from Products.ATContentTypes.utils import DT2dt
import datetime
from operator import sub, gt
from Products.CMFCore.utils import getToolByName
from iqpp.clickcounting.interfaces import IClickCounting
from zbw.ejStats.utils import format_number

# we could use chain.from_iterable here, but toolz.concat is shorter (and uses
# chain.from_iterables)
# from itertools import chain
from toolz.itertoolz import concat
from toolz.functoolz import pipe
from toolz.dicttoolz import keymap


def clickcount(obj):
    cc = IClickCounting(obj)
    return cc.getClicks()


def average(papers, downloads):
    # avg = lambda dl: {gt(dl, 0): div(dl, papers), eq(dl, 0): 0}.get(True)
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
        if 'days' not in self.request or self.request['days'] == "":
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
        delta = int(self.request['days'])
        # convert old Zope DateTime to python datetime
        obj_date = DT2dt(created).replace(tzinfo=None)
        d = datetime.timedelta(days=delta)
        return len(filter(lambda date: gt(obj_date, sub(date, d)), dates))

    @memoize
    def __dl_over_time(self):
        """
        get a sorted dictionary with month as key
        """
        # XXX can we do this more functional?
        def update_dic(obj):
            dates = annotations(obj)
            for key in dates.keys():
                count = len(dates[key])
                dl[key]['Sum'] += count
                dl[key][obj.portal_type] += count
                dl[key]['new'] += self.__was_new(dates[key], obj.created())

        annotations = lambda obj: IAnnotations(obj)['hbxt.clickdates']
        dates = map(annotations, self.get_clickdates_objects())
        keyse = concat(map(lambda date: map(lambda k: k, date.keys()), dates))
        dl = {k: {'Sum': 0, 'new': 0, 'JournalPaper': 0,
            'DiscussionPaper': 0} for k in keyse}
        map(update_dic, self.get_clickdates_objects())
        return keymap(add_leading_zero, dl)
        
    def dl_listed(self):
        """
        """
        dl_sorted = self.__dl_over_time()
        months = sorted(dl_sorted.iterkeys(), reverse=True)
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


