# Calibre LCPL Input plugin

## General usage

This plugin allows you to fulfill LCPL book license files for books protected with Readium LCP DRM. Just add this plugin to Calibre, then add an LCPL book license file to Calibre. That file will then turn into a LCP DRM protected eBook which you can send to your Tolino eBook reader.

## Settings

This plugin has just three different settings: 

- It allows you to set a custom user agent. Out of the box, it uses a Chrome user agent that matches your OS, to make the download look like a legit download through a web reader. If you want to use a different one you can enter that in the settings. 
- It allows you to ignore content errors. By default, it verifies the resulting EPUB file to make sure it's correct (correct file size, correct SHA256 hash, ...). If the LCPL file is corrupted and contains an invalid hash, or there was an issue while downloading that corrupted the book, the downloaded file will be deleted and you can try again. If needed, this validation can be disabled. 
- It allows you to skip the validity verification. By default, the plugin refuses to download books where the license file is not yet valid, or no longer valid (like for library books). You can disable this verification (as the book might still be available on the server for download), but then the book provider will know you're on a nonstandard client.

## DRM information

Note: All eBooks downloaded / added with this plugin will still keep the Readium LCP DRM protection. This plugin only turns a LCP license file (LCPL file) into an LCP-protected EPUB or PDF, it does not get rid of the DRM. 

To my knowledge there's no public software (yet) that can remove the DRM from Readium LCP eBooks, though it should be possible (easier than for Adobe DRM eBooks, IMHO) to create such software. 

I am not going to do that, though, as I don't want to get into legal trouble. Maybe someone else does. 