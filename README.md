# shutterrip.py: A Shutterfly Share Sites Download Tool

## Who this is for

This is for people who are affected by the upcoming shutdown of Shutterfly share sites
who have pictures they wish to download, but who don't want to go through and download
them one-by-one.

## What does it do

Using Selenium and chromedriver.exe, it manages the tedium for you:

It:
 * Logs into Shutterfly
 * Enumerates all the albums on each configured site (see usage notes)
 * Enumerates all the pictures for each album
 * Downloads each picture

Pictures are downloaded into a file structure which looks something like this:

```
SITE/
  [#]_ALBUM/
    [#]_<METADATA>.jpg
```

It automatically sanitizes album and metadata strings to work as NTFS file names
(for the Windows users out there), 

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

Again, there is NO WARRANTY and NO SUPPORT for this code in any way, shape or form!

(I'm sharing this upon request of a coworker, and while I'm happy if others find use in it, I have
no intent of replying to any issues filed with it.)


## Usage notes



To be written