#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Calibre plugin for Readium LCP "LCPL" files. 
# This basically "converts" an LCPL license file into an EPUB (or PDF). 
# Note that this does NOT remove the LCP DRM from the files. 
# It just turns an LCPL license file into an eBook. 

# To my knowledge there's no public program (yet) that can
# remove the DRM from Readium LCP eBooks, though it should
# be possible (easier than for Adobe DRM eBooks) to create
# such a program. 

# I am not going to do that, though, as I don't want to 
# get into legal trouble.


# Revision history: 
# v0.0.1: First public version

from calibre.customize import FileTypePlugin        # type: ignore
__version__ = '0.0.1'

PLUGIN_NAME = "LCPL Input"
PLUGIN_VERSION_TUPLE = tuple([int(x) for x in __version__.split(".")])
PLUGIN_VERSION = ".".join([str(x)for x in PLUGIN_VERSION_TUPLE])


# Ton of libraries

import json
import os
import hashlib
import urllib.request
import dateutil.parser
import datetime
import traceback
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
from contextlib import closing


class LCPLInput(FileTypePlugin):
    name                        = PLUGIN_NAME
    description                 = "Downloads LCP-encrypted books from a LCPL license file. Note: This does not remove the LCP DRM."
    supported_platforms         = ['linux', 'osx', 'windows']
    author                      = "Leseratte10"
    version                     = PLUGIN_VERSION_TUPLE
    minimum_calibre_version     = (5, 0, 0)
    file_types                  = set(['lcpl'])
    on_import                   = True
    on_preprocess               = True
    priority                    = 900

    def initialize(self): 
        # Patch Calibre to consider "LCPL" a book. This makes LCPL files show up
        # in the "Add Book" file selection, and it also makes the auto-add feature useable.
        try: 
            from calibre.ebooks import BOOK_EXTENSIONS
            if ("lcpl" not in BOOK_EXTENSIONS):
                BOOK_EXTENSIONS.append("lcpl")
        except:
            print("{0} v{1}: Couldn't add LCPL to book extension list:".format(PLUGIN_NAME, PLUGIN_VERSION))
            traceback.print_exc()

    def is_customizable(self):
        return True

    def config_widget(self):
        import calibre_plugins.lcplinput.config as config   # type: ignore
        return config.ConfigWidget(self.plugin_path)

    def parseLCPLdownloadBook(self, lcpl_string: str):

        import calibre_plugins.lcplinput.prefs as prefs     # type: ignore
        settings = prefs.LCPLInput_Prefs()

        # This function is called by the run function when it encounters an LCP license file
        try: 
            license = json.loads(lcpl_string)
            print("{0} v{1}: Found LCPL for book ID {2}".format(PLUGIN_NAME, PLUGIN_VERSION, license["id"]))
        except: 
            print("{0} v{1}: LCPL license file invalid".format(PLUGIN_NAME, PLUGIN_VERSION))
            return None

        lic_start = None
        lic_end = None

        if ("rights" in license and "start" in license["rights"]):
            lic_start = dateutil.parser.isoparse(license["rights"]["start"])

        if ("rights" in license and "end" in license["rights"]):
            lic_end = dateutil.parser.isoparse(license["rights"]["end"])

        currenttime = datetime.datetime.now(datetime.timezone.utc)

        is_in_license_range = True

        if lic_start is not None: 
            if lic_start > currenttime:
                is_in_license_range = False
        if lic_end is not None:
            if lic_end < currenttime:
                is_in_license_range = False

        if not is_in_license_range: 
            print("{0} v{1}: WARNING: LCPL license expired (valid from {2} until {3})".format(PLUGIN_NAME, PLUGIN_VERSION, str(lic_start), str(lic_end)))

            if settings["honor_license_time_limits"]:
                return None
            else: 
                print("{0} v{1}: User decided to override, try downloading anyways ...".format(PLUGIN_NAME, PLUGIN_VERSION))


        dl_link = None
        dl_size = 0
        dl_sha256_hash = None
        dl_is_buggy_template = False

        for link in license["links"]: 
            if (
                (link["rel"] == "publication" and link["type"] == "application/epub+zip") or
                (link["rel"] == "publication" and link["type"] == "application/pdf")
            ):
                dl_link = link["href"]
                if "length" in link:
                    dl_size = link["length"]
                if "hash" in link:
                    dl_sha256_hash = link["hash"].lower()

                if link["type"] == "application/epub+zip":
                    dl_file_name_ext = ".epub"
                elif link["type"] == "application/pdf":
                    dl_file_name_ext = ".pdf"
                else:
                    dl_file_name_ext = ".zip"

                # Check for templating:
                if ("templated" in link and ((link["templated"] is True) or (link["templated"].lower() == "true"))):
                    # This is a templated URL. The license server is supposed to fix this, but you never know
                    # TODO: Not sure if this should be a Bool or a String ...
                    print("[ * ] Found templated URL - this is not supposed to happen. Will try to fix this ...")
                    dl_is_buggy_template = True
                
                
                break
        
        if dl_link is None: 
            print("{0} v{1}: No download link found in LCPL".format(PLUGIN_NAME, PLUGIN_VERSION))
            return None
      
        # Download book: 

        if settings["use_custom_ua"] and settings["useragent"] != "":
            ua = settings["useragent"]
            print("{0} v{1}: Downloading book from {2} with custom UA ...".format(PLUGIN_NAME, PLUGIN_VERSION, dl_link))
        else:
            # Get default UA that matches the OS
            ua = settings.get_system_ua()                
            print("{0} v{1}: Downloading book from {2} with default UA ...".format(PLUGIN_NAME, PLUGIN_VERSION, dl_link))

        outputname = self.temporary_file(dl_file_name_ext).name

        
        try:
            req = urllib.request.Request(url=dl_link, headers={'User-Agent': ua})
            handler = urllib.request.urlopen(req)
            chunksize = 16 * 1024

            ret_code = handler.getcode()

            if ret_code != 200:
                print("{0} v{1}: Download returned error {2}".format(PLUGIN_NAME, PLUGIN_VERSION, ret_code))
                raise Exception("DL error") 

            with open(outputname, "wb") as f:
                while True:
                    chunk = handler.read(chunksize)
                    if not chunk:
                        break
                    f.write(chunk)

        except Exception as e:
            if dl_is_buggy_template:
                print("{0} v{1}: Downloading book failed, try templating ...".format(PLUGIN_NAME, PLUGIN_VERSION))
            else: 
                print("{0} v{1}: Downloading book failed!".format(PLUGIN_NAME, PLUGIN_VERSION))
                return None

            dl_link2 = dl_link.replace("{license_id}", license["id"])
            if (dl_link2 != dl_link):
                try:
                    req = urllib.request.Request(url=dl_link2, headers={'User-Agent': ua})
                    handler = urllib.request.urlopen(req)
                    chunksize = 16 * 1024

                    ret_code = handler.getcode()

                    if ret_code != 200:
                        print("{0} v{1}: Download returned error {2}".format(PLUGIN_NAME, PLUGIN_VERSION, ret_code))
                        raise Exception("DL error") 

                    with open(outputname, "wb") as f:
                        while True:
                            chunk = handler.read(chunksize)
                            if not chunk:
                                break
                            f.write(chunk)

                except Exception as e:
                    print("{0} v{1}: Downloading book failed even with templating".format(PLUGIN_NAME, PLUGIN_VERSION))
                    return None
            else: 
                print("{0} v{1}: Templating enabled but not used.".format(PLUGIN_NAME, PLUGIN_VERSION))
                return None


        try: 
            total_length = int(req.headers.get('content-length'))
        except: 
            total_length = None

        # Download done, check length: 

        if (dl_size > 0 and os.path.getsize(outputname) != dl_size): 
            print("{0} v{1}: Invalid file length (LCPL file said {2} but server sent {3})".format(PLUGIN_NAME, PLUGIN_VERSION, dl_size, os.path.getsize(outputname)))
            if (not settings["ignore_content_errors"]): 
                return None

        if (total_length is not None and total_length > 0 and os.path.getsize(outputname) != total_length):
            print("{0} v{1}: Invalid file length (server said {2} but actually sent {3})".format(PLUGIN_NAME, PLUGIN_VERSION, total_length, os.path.getsize(outputname)))
            if (not settings["ignore_content_errors"]): 
                return None

        # Check hash
        if (dl_sha256_hash is not None):
            hash = hashlib.sha256()

            with open(outputname, "rb") as f:
                while True:
                    data = f.read(8192)
                    if not data: 
                        break
                    hash.update(data)
            
            actual_hash = hash.hexdigest().lower()

            if (dl_sha256_hash != actual_hash):
                print("{0} v{1}: File SHA256 hash invalid".format(PLUGIN_NAME, PLUGIN_VERSION))
                if (not settings["ignore_content_errors"]): 
                    return None

        # Write book to file system: 
        try: 
            # Inject license file
            with closing(ZipFile(outputname, 'a')) as outfile: 
                outfile.writestr("META-INF/license.lcpl", lcpl_string)
        except: 
            print("{0} v{1}: Error while writing output file".format(PLUGIN_NAME, PLUGIN_VERSION))
            return None

        return outputname
    

    def run(self, path_to_ebook: str):
        # This code gets called by Calibre with a path to the new book file. 
        # Check if it's actually a valid LCPL file.

        print("{0} v{1}: Trying to parse file {2}".format(PLUGIN_NAME, PLUGIN_VERSION, os.path.basename(path_to_ebook)))

        ftype = None
        
        # Check file type: 
        with open(path_to_ebook, "rb") as bookfile:
            dataSTR = bookfile.read().decode('latin-1')

    
        try: 
            json_str = json.loads(dataSTR)
            if ("id" in json_str and "encryption" in json_str and "profile" in json_str["encryption"]): 
                ftype = "LCPL"
                print("{0} v{1}: Looks like this is a LCPL license file".format(PLUGIN_NAME, PLUGIN_VERSION))
        except: 
            pass

        # Okay, once we're here, ftype is either "LCPL" or None.

        if ftype is None: 
            print("{0} v{1}: Looks like this file isn't supported by {0}".format(PLUGIN_NAME, PLUGIN_VERSION))
            return path_to_ebook

        elif ftype == "LCPL":
            destination = self.parseLCPLdownloadBook(dataSTR)

            if (destination is not None):
                return destination


        print("{0} v{1}: Failed, return original ...".format(PLUGIN_NAME, PLUGIN_VERSION))
        return path_to_ebook



