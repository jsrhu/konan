#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
lib.data.py
Created on Tue Feb 14 12:39 2017
@author: Joshua Hu

///////////
Constants**
///////////
None

/////////
Classes**
/////////
Parent:

Children:

"""
from __future__ import print_function

from abc import ABCMeta, abstractmethod

import sys
import datetime
import os, os.path
import datetime as dt
import operator as op

import numpy as np
import pandas as pd
from tqdm import tqdm
import traceback

import readWriteData as rwd
import directory as dr

class Repository(object):
    def __init__(self, path_root = '', project = '', data_file = ''):
        self._root = path_root #find users Dropbox folder

        self._projects = os.listdir(self.root)
        self._current_project = self.selectProject(project = project)

        self._current_file = data_file

        self._special_files = {}

    def root():
        doc = "The root property."
        def fget(self):
            return self._root
        def fset(self, value):
            self._root = value
        def fdel(self):
            del self._root
        return locals()
    root = property(**root())

    def projects():
        doc = "The projects property."
        def fget(self):
            return self._projects
        def fset(self, value):
            self._projects = value
        def fdel(self):
            del self._projects
        return locals()
    projects = property(**projects())

    def current_project():
        doc = "The current_project property."
        def fget(self):
            return self._current_project
        def fset(self, value):
            self._current_project = value
        def fdel(self):
            del self._current_project
        return locals()
    current_project = property(**current_project())

    def current_file():
        doc = "The current_file property."
        def fget(self):
            if self.checkData(self._current_file):
                return self._current_file
            else:
                return self.checkData(self._current_file)
        def fset(self, value):
            self._current_file = value
        def fdel(self):
            del self._current_file
        return locals()
    current_file = property(**current_file())

    def project_path():
        doc = "The project_path property."
        def fget(self):
            return self.root + self.current_project
        return locals()
    project_path = property(**project_path())

    def file_path():
        doc = "The file_path property."
        def fget(self):
            return self._root + self._current_project + self._current_file
        return locals()
    file_path = property(**file_path())

    def special_files():
        doc = "The special_files property."
        def fget(self):
            return self._special_files
        def fset(self, value):
            self._special_files = value
        def fdel(self):
            del self._special_files
        return locals()
    special_files = property(**special_files())

    def selectProject(self, project = ''):
        if dr.checkPath(path = self.root+project, is_file = False) and project in self.projects:
            return project
        else:
            print("Error retrieving project.\nCheck the path.")
            return ''

    def markSpecialFile(self, key = '', path_file = ''):
        self.special_files[key] = path_file

    class Path(object):
        """docstring for Path."""
        def __init__(self, name = '', extension = '/', children = []):
            super(Path, self).__init__()
            self._name = name
            self._extension = extension
            self._children = children

        def __repr__(self):
            return self.name + self.extension

        def name():
            doc = "The name property."
            def fget(self):
                return self._name
            def fset(self, value):
                self._name = value
            def fdel(self):
                del self._name
            return locals()
        name = property(**name())

        def extension():
            doc = "The extension property."
            def fget(self):
                return self._extension
            def fset(self, value):
                self._extension = value
            def fdel(self):
                del self._extension
            return locals()
        extension = property(**extension())

        def children():
            doc = "The children property."
            def fget(self):
                return self._children
            def fset(self, value):
                self._children = value
            def fdel(self):
                del self._children
            return locals()
        children = property(**children())

        def add_child(self, node):
            assert isinstance(node, Tree)
            self.children.append(node)


class Filter(object):
    """
    Base Class for data filters. Historical Filter for Backtest sub-system and Live Filter for Live Trading sub-system
    """
    def __init__(self, filter_lifespan = 1, filter_update_period = 1, hist_data_sources = [], live_data_sources = [], **kwds):
        """
        Constructor for dataFilter class

        Parameters:
        self -
        filter_lifespan -
        filter_update_period -
        hist_data_sources -
        live_data_sources -

        Return:
        None
        """

        self._lifespan = dt.timedelta(days=filter_lifespan)
        self._update_period = dt.timedelta(days=filter_update_period)
        self._hist_data_sources = hist_data_sources
        self._live_data_sources = live_data_sources

    @property
    def lifespan(self):
        return self._lifespan

    @lifespan.setter
    def lifespan(self, value):
        if value < 1:
            raise ValueError("Filter Lifespan must be at least 1 day long, i.e. Lifespan must be non-zero and positive")
        if not isinstance(value,(int,long)):
            raise TypeError("Filter Lifespan must be set in whole days, i.e. Lifespan value must be an integer")
        self._lifespan = dt.timedelta(days=value)

    @property
    def update_period(self):
        return self._update_period

    @update_period.setter
    def update_period(self, value):
        if value < 1:
            raise ValueError("Filter Update Period must be at least 1 day long, i.e. Update Period must be non-zero and positive")
        if not isinstance(value,(int,long)):
            raise TypeError("Filter Update Period must be set in whole days, i.e. Update Period value must be an integer")
        self._update_period = dt.timedelta(days=value)

    @property
    def hist_data_sources(self):
        return self._hist_data_sources

    @hist_data_sources.setter
    def hist_data_sources(self, sources):
        #raise error on object types in list?
        if sources == None:
            raise ValueError("Source list cannot be empty")
        self._hist_data_sources = sources

    @property
    def live_data_sources(self):
        return self._live_data_sources

    @live_data_sources.setter
    def live_data_sources(self, sources):
            #raise error on object types in list?
        if sources == None:
            raise ValueError("Source list cannot be empty")
        self._live_data_sources = sources

    def rawFilter(self, data = pd.DataFrame(), columns = [], black = False):
        """
        Filter raw data to create a pandas DataFrame

        Parameters:
        data -
        columns -
        black -

        Return:
        function - returns pandas DataFrame
        """
        if black == True:
            return self._rawBlacklist(data = data, columns = columns)
        else:
            return self._rawWhitelist(data = data, columns = columns)

    def _rawBlacklist(self, data = pd.DataFrame(), columns = []):
        """
        Private function for filter class that returns a subsection of a pandas DataFrame using a blacklist of DataFrame columns.

        Parameters:
        columns -

        Return:
        df - pandas DataFrame
        """
        df = rwd.readToDF(path_data = data)
        filtered = df.drop(labels = columns, axis = 1)
        return filtered

    def _rawWhitelist(self, data = pd.DataFrame(), columns = []):
        """
        Private function for filter class that returns a subsection of a pandas DataFrame using a whitelist of DataFrame columns.

        Parameters:
        columns -

        Return:
        df - pandas DataFrame
        """
        df = rwd.readToDF(path_data = data)
        filtered = df[columns]
        return filtered

    def rawValueFilter(self, data = pd.DataFrame(), columns = [], values = {}, comparators = {}):
        """
        Filter raw data to create a pandas DataFrame

        Parameters:
        data - pandas DataFrame
        columns - columns to filter
        values - dictionary with column names as strings and values being the values to filter by
        comparator - comparison operator

        Return:
        function - returns pandas DataFrame
        """
        dict_comparator = {'!=':op.ne,
                           '==':op.eq,
                           '<':op.lt,
                           '>':op.gt,
                           '<=':op.le,
                           '>=':op.ge}
        #try catch for not comparators
        df = data
        for key in columns:
            df_new = df[dict_comparator[comparators[key]]( df[key] , values[key] )]
            df = df_new
        return df

    def rawSetFilter(self, data = pd.DataFrame(), set_ = [], columns = [], black = False):
        """
        PARAMETERS:
        self -
        data -
        set_ -
        columns -
        black -

        RETURN:
        df - filteres pandas DataFrame
        """
        df = data
        for key in columns:
            df_new = df[df[key].isin(set_)]
            df = df_new
        return df

    def calcFilter(self, data = pd.DataFrame(), columns = [], functions = [], black = False):
        """
        Filter raw data through the use of a calculated function from the data properties

        Parameters:
        data -
        columns -
        functions -
        black -

        Return:
        function - returns pandas DataFrame
        """
        if black == True:
            return self._calcBlacklist(data = data, columns = columns, functions = functions)
        else:
            return self._calcWhitelist(data = data, columns = columns, functions = functions)

    def _calcBlacklist(self, data = pd.DataFrame(), columns = [], functions = []):
        """
        Private function for filter class that returns a subsection of a pandas DataFrame using functions to create a blacklist of DataFrame columns.

        Parameters:
        data -
        columns -
        functions -

        Return:
        df - pandas DataFrame
        """
        for function in functions:
            df = function(data,inplace=True)
        return df

    def _calcWhitelist(self, data = pd.DataFrame(), columns = [], functions = []):
        """
        Private function for filter class that returns a subsection of a pandas DataFrame using functions to create a blacklist of DataFrame columns.

        Parameters:
        data -
        columns -
        functions -

        Return:
        df - pandas DataFrame
        """
        for function in functions:
            df = function(data,inplace=True)
        return df

class HistoricalFilter(Filter):
    """
    Historical Filter for Backtest sub-system
    """
    def __init__(self, filter_lifespan = 1, filter_update_period = 1, **kwds):
        """
        Constructor for histFilter class

        Parameters:
        self -
        filter_lifespan -
        filter_update_period -

        Return:
        None
        """
        base = Filter(filter_lifespan = filter_lifespan, filter_update_period = filter_update_period, hist_data_sources = [])
        self._lifespan = base.lifespan
        self._update_period = base.update_period
        self._hist_data_sources = base.hist_data_sources

    def spawnLiveFilter(self):
        return LiveFilter(filter_lifespan = self.lifespan, filter_update_period = self.filter_update_period)

class LiveFilter(Filter):
    """
    Live Filter for Live trading sub-system
    """
    def __init__(self, filter_lifespan = 1, filter_update_period = 1, update_hour = 16, update_minute = 00, dict_candidate = {'candidate_columns':[],'candidate_values':{}, 'candidate_comparators':{}}, dict_whitelist = {'whitelist_columns':[],'whitelist_values':{}, 'whitelist_comparators':{}}, columns = [], candidate_values = {}, whitelist_values ={}, comparators = {}, **kwds):
        """
        Constructor for liveFilter class

        Parameters:
        self -
        filter_lifespan -
        filter_update_period -

        Return:
        None
        """
        base = Filter(filter_lifespan = filter_lifespan, filter_update_period = filter_update_period, live_data_sources = [])
        self._lifespan = base.lifespan
        self._update_period = base.update_period
        self._live_data_sources = base.live_data_sources
        self._birthdate = dt.date.today()
        self._update_time = dt.time(hour = update_hour, minute = update_minute)

        self._candidate_columns = dict_candidate['candidate_columns']
        self._candidate_values = dict_candidate['candidate_values']
        self._candidate_comparators = dict_candidate['candidate_comparators']

        self._whitelist_columns = dict_whitelist['whitelist_columns']
        self._whitelist_values = dict_whitelist['whitelist_values']
        self._whitelist_comparators = dict_whitelist['whitelist_comparators']

    @property
    def birthdate(self):
        return self._birthdate

    @property
    def update_time(self):
        return self._update_time

    @property
    def candidate_columns(self):
        return self._candidate_columns

    @property
    def candidate_values(self):
        return self._candidate_values

    @property
    def candidate_comparators(self):
        return self._candidate_comparators

    @property
    def whitelist_columns(self):
        return self._whitelist_columns

    @property
    def whitelist_values(self):
        return self._whitelist_values

    @property
    def whitelist_comparators(self):
        return self._whitelist_comparators

    def _check(self):
        time_now = dt.datetime.now().time()
        if time_now >= self.update_time:
            return True
        else:
            return False

    def updateCandidateList(self, data = pd.DataFrame(), columns = []):
        """
        Parameters:
        self
        data

        Return:
        df_candidate_update
        """
        if not self._check():
            pass
        else:
            df_candidate_update = self.rawValueFilter(data = data, columns = self.candidate_columns, values = self.candidate_values, comparators = self.candidate_comparators)
            return df_candidate_update

    def updateWhitelist(self, data = pd.DataFrame(), columns = []):
        """
        Parameters:
        self
        data

        Return:
        df_whitelist_update
        """
        if not self._check(): # causing errors if day parameters of _check() are not specified
            pass
        else:
            df_whitelist_update = self.rawValueFilter(data = data, columns = self.whitelist_columns, values = self.whitelist_values, comparators = self.whitelist_comparators)
            return df_whitelist_update

    def connect(self, source):
        """
        Connect to a given data source.

        Parameters:
        source

        Return:
        connection
        """
        connection = source
        return connection

    def readConnection(self, connection):
        """
        Read information form a connection to a data source.

        Parameters:
        connection

        Return:
        data
        """
        data = connection
        return data
