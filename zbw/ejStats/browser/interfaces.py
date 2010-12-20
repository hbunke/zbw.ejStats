# -*- coding: UTF-8 -*-
# Dr. Hendrik Bunke, h.bunke@zbw.eu

# provides statistics of economics papers

#TODO citations unterschieden nach dp und ja

from zope.interface import Interface


class IStatView(Interface):
    """
    provides methods for analyzing several economics 'numbers'
    """
        
    def get_all_papers():
        """
        returns all papers to be examined from the catalog
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

    
    def countReaders():
        """number of registered readers
        """

    def countRecommended():
        """number of recommendations and articles recommended
        """


    def countAuthors():
        """counts number of authors
        """

    def countCitations():
        """sums all Citec Citations
        """

    def maxCitations():
        """reutrns most cited papers
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

    def count_crossref_citations():
        """
        returns number of citations at crossref (local query)
        """

    def articles_with_citations():
        """returns all articles with crossref citations
        """

    def cited_in():
        """
        returns Journal
        """


