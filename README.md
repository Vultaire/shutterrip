# shutterrip.py: A Shutterfly Share Sites Download Tool

## License

    shutterrip.py: A Shutterfly share sites downloading script.
    Copyright (C) 2023 Paul Goins

    This program is free software: you can redistribute it and/or modify
    it under the terms of version 3 of the GNU General Public License as
    published by the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

See LICENSE.txt to see the full license text.

## Who this is for

This is for people who are affected by the upcoming shutdown of Shutterfly share sites
who have pictures they wish to download, but who don't want to go through and download
them one-by-one.  This script will effectively do so for you, using Python-driven
browser automation via the Selenium library and Chromedriver.

## What does it do

It:
 * Logs into Shutterfly
 * Enumerates all the albums on each configured site (see usage notes)
 * Enumerates all the pictures for each album
 * Downloads each picture

Pictures are downloaded into a file structure which looks something like this:

```
SITE_LINK/
  [#]_ALBUM/
    [#]_<METADATA>.jpg
```

It automatically sanitizes the site, album and metadata strings in an NTFS-friendly way.  It
should easily run on Windows and non-Windows systems, as long as there is a Python 3 interpreter
available to run the script.

## Who this is NOT for

If you have access to the pictures in question in a way other than via the share sites,
it may be better to use  Shutterfly's other interfaces which allow for downloading multiple
files in one go.  This is meant for people who only have access to the pictures via share sites.

I also assume that you are comfortable running Python code, comfortable writing configuration
files, comfortable following directions, and comfortable with fixing things if they break.  I'm
providing zero support for this.  If this does not describe you, this is not for you; sorry.

You should also be comfortable reading or at least skimming source code.  This code uses your
Shutterfly credentials and logs in using them.  Don't trust random code off the Internet for
this job!  Read the code and only use it if you feel comfortable with what the code is doing!!!

If you need to download videos, note that this script is not designed for that; you will need
to write code to extend this script.

Again, there is NO WARRANTY and NO SUPPORT for this code in any way, shape or form!

(I'm sharing this upon request of a coworker, and while I'm happy if others find use in it, I have
no intent of replying to any issues filed with it.)

## Usage notes

### The "Too long; didn't read" version

Copy config.yaml.example to config.yaml, update it as necessary, and download Chromedriver if you
don't already have it.  Install the prerequisites in requirements.txt, then run "python shutterrip.py"
(or "python3 shutterrip.py") with no arguments.

### Specifying site links

The main use case for this is for downloading the "Pictures" section from the "Pictures & Videos"
tab of a share site.  If you click on "Pictures & Video", you will be taken to a summary page
which may or may not have all your albums available; click the "Pictures" header to be taken to the
"Pictures" subsection.  (For the share sites I've cloned, the URL for this page typically ends in
"/pictures/8" rather than just "/pictures".)  You will want to copy this URL into config.yaml under
the "site_links" section.

It can also be used for other folders containing pictures.  Navigate to whatever page contains the
albums you wish to download, then ensure that all the albums you wish to download can be shown from
that page.  Like above, copy the URL into the config.yaml under "site_links".

I have not tried to download any videos, so while it may work for video sections as well, I have not
tested this.

### Other requirements

You will need to provide your Shutterfly email and password in config.yaml.  As doing so with
untrusted code is potentially dangerous, please **READ THE SOURCE CODE** and judge for yourself
whether you trust this script to use your credentials.  Again, there is NO WARRANTY on this script
and any risk in running it is assumed by the user.

You will also require Google Chrome (or Chromium) to be installed, as well as an appropriate
version of Chromedriver, which is how Selenium controls Google Chrome in this script.  Specify
the path to the Chromedriver executable in config.yaml.  If on Windows, make sure to use single
quotes around the string so the \ characters are not escaped.

## Notes about reliability

Note that this script is known not to work flawlessly - if pages take too long to render, or
downloads take too long to run, or in some other corner cases which haven't fully been teased
out, it is known to fail.  I have coded in resume and retry logic to mitigate this, but please
keep in mind that this is effectively a quick hack for a personal problem I had to solve in
short order.  Feel free to improve upon this if you need.  That being said, it was good enough
for me to be able to download over 13,000 files off the shares I needed to pull files from.

Also note that this doesn't automatically search for all possible folders of albums on a share
site - you need to provide the URLs to the pages providing the albums; the script will recurse
from there to pull the albums and their pictures.

## Notes about Shutterfly terms of service

I do not know if this violates Shutterfly's terms of service.  It is not my intention to do so.
While I think it would be very unfortunate for something like this to be deemed against their
TOS, especially as share sites do not appear to allow for any sort of multiple file download
functionality, please note that use of this script is at your own risk and I take no
responsibility if use of this script is seen as such a violation.