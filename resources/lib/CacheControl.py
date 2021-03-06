'''
Class: CacheControl

Author: Hippojay (kodex@h-jay.com)
Version: 1
Requires: Kodex/Plexbmc

Implementation of file based caching for python objects.  
Utilises pickle to store object data as file within the KODI virtual file system.

'''
import xbmcvfs
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle

from common import *

printDebug=printDebug("PleXBMC", "cachecontrol")    

class CacheControl:

    def __init__(self, cache_location, enabled=True):

        self.cache_location=cache_location        
        self.enabled=enabled

        if self.enabled:

            if self.cache_location[-1] != "/":
                self.cache_location+="/"

            if not xbmcvfs.exists(self.cache_location): 
                printDebug.debug("CACHE [%s]: Location does not exist.  Creating" % self.cache_location)
                if not xbmcvfs.mkdirs(self.cache_location):
                    printDebug.debug("CACHE [%s]: Location cannot be created" % self.cache_location)
                    self.cache_location=None
                    return
            printDebug.debug("Running with cache location: %s" % self.cache_location)

        else:
            self.cache_location=None
            printDebug.debug("Cache is disabled")

    def readCache(self, cache_name):
        if self.cache_location is None:
            return (False, None)

        printDebug.debug("CACHE [%s]: attempting to read" % cache_name)
        try:
            cache=xbmcvfs.File(self.cache_location+cache_name)
            cachedata = cache.read()
            cache.close()
        except Exception, e:
            printDebug.debug("CACHE [%s]: read error [%s]" % ( cache_name, e))

        if cachedata:
            printDebug.debug("CACHE [%s]: read" % cache_name)
            printDebug.debugplus("CACHE [%s]: data: [%s]" % ( cache_name, cachedata))
            cacheobject = pickle.loads(cachedata)
            return (True, cacheobject)

        printDebug.debug("CACHE [%s]: empty" % cache_name)
        return (False, None)

    def writeCache(self,cache_name,object):

        if self.cache_location is None:
            return True

        printDebug.debug("CACHE [%s]: Writing file" % cache_name)
        try:
            cache=xbmcvfs.File(self.cache_location+cache_name,'w')
            cache.write(pickle.dumps(object))
            cache.close()
        except Exception, e:
            printDebug.debug("CACHE [%s]: Writing error [%s]" % (self.cache_location+cache_name, e))

        return True

    def checkCache(self,cache_name, life=3600):

        if self.cache_location is None:
            return (False, None)

        if xbmcvfs.exists(self.cache_location+cache_name):
            printDebug.debug("CACHE [%s]: exists" % cache_name)
            now = int(round(time.time(),0))
            modified = int(xbmcvfs.Stat(self.cache_location+cache_name).st_mtime())
            printDebug.debug ("CACHE [%s]: mod[%s] now[%s] diff[%s]" % ( cache_name, modified, now, now - modified))

            if ( modified < 0) or ( now - modified ) > life:
                printDebug.debug("CACHE [%s]: too old, delete" % cache_name)

                if xbmcvfs.delete(self.cache_location+cache_name):
                    printDebug.debug("CACHE [%s]: deleted" % cache_name)
                else:
                    printDebug.debug("CACHE [%s]: not deleted" % cache_name)
            else:
                printDebug.debug("CACHE [%s]: current" % cache_name)

                return self.readCache(cache_name)
        else:
            printDebug.debug("CACHE [%s]: does not exist" % cache_name)

        return (False, None)

    def deleteCache(self, force=False):
        printDebug.debug("== ENTER: deleteCache ==")
        cache_suffix = ".cache"
        persistant_cache_suffix = ".pcache"
        dirs, file_list = xbmcvfs.listdir(self.cache_location)

        printDebug.debug("List of file: [%s]" % file_list)
        printDebug.debug("List of dirs: [%s]" % dirs)

        for file in file_list:

            if force and persistant_cache_suffix in file:
                printDebug("Force deletion of persistent cache file")
            elif cache_suffix not in file:
                continue

            if xbmcvfs.delete(self.cache_location+file):
                printDebug.debug("SUCCESSFUL: removed %s" % file)
            else:
                printDebug.debug("UNSUCESSFUL: did not remove %s" % file )
