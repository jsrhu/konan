#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
////////////////////////////////////////////////

dataHandler.py
Created on Tue Oct 25 09:52 2016
@author: jsrhu

CLASS FILE

////////////////////////////////////////////////
------------------------------------
Packages
------------------------
STDLIB:
datetime
operators

MAINTAINED:
pandas
tqdm

CUSTOM:
lib.readWriteData

------------------------------------
Constants
------------------------
Integers: int
------------

------------------------
Long: long
------------

------------------------
Floats: float
------------

------------------------
Complex: complex
------------

------------------------
Strings: str
------------

------------------------
Arrays: list
------------

------------------------
Tuple: (x,y)
------------

------------------------
Sets: set
------------

------------------------
Frozen Set: frozenset
------------

------------------------
Dictionary: {'x':x,'y':y}
------------

------------------------------------
Classes
------------------------
dataFilter
------------
histFilter
liveFilter

------------------------
storage
------------

------------------------
analyzer
------------

------------------------------------
Functions
------------------------
Public
------------

------------------------
Private
------------

////////////////////////////////////////////

TODO:

////////////////////////////////////////////////
"""
import datetime as dt
import operator as op

import pandas as pd
from tqdm import tqdm

import lib.readWriteData as rwd

class dataFilter(object):
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

class histFilter(dataFilter):
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
        base = dataFilter(filter_lifespan = filter_lifespan, filter_update_period = filter_update_period, hist_data_sources = [])
        self._lifespan = base.lifespan
        self._update_period = base.update_period
        self._hist_data_sources = base.hist_data_sources

    def spawnLiveFilter(self):
        return liveFilter(filter_lifespan = self.lifespan, filter_update_period = self.filter_update_period)

class liveFilter(dataFilter):
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
        base = dataFilter(filter_lifespan = filter_lifespan, filter_update_period = filter_update_period, live_data_sources = [])
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

class storage(object):
    """
    Storage for unanalyzed data.
    """
    def __init__(self):
        """
        Constructor for storage.

        Parameters:
        self

        Return:
        None
        """
        pass

class analyzer(object):
    """
    Analyzer for unanalyzed data.

    """
    def __init__(self):
        """
        Constructor for analyzer.

        Parameters:
        self

        Return:
        None
        """
        pass
