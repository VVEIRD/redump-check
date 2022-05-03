# redump-check
Tests a collection against a redump.org dat file

## Howto

Download a dat file from redump.org, and use it to check a collection:

    C:\path\to\script\redump-check D:\path\to\collection "D:\Sony - PlayStation - Datfile (10649) (2022-05-02 09-44-32).dat"

The scripts output will look something like this:

    ~~~ Redump Collection Verifier ~~~
    ~~ Verifies any redump dat      ~~
    ~~  files against a collection  ~~
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    ~~           Settings           ~~
    ~~ DAT File: D:\Sony - PlayStation - Datfile (10649) (2022-05-02 09-44-32).dat
    ~~ ROM Folder: D:\path\to\collection
    ~~ Allowed Extensions: .cue, .bin
    ~~ Recursive: Yes
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Checking Games:
    - Dump 1
      * Error on file Dump 1.cue - md5 missmatch: n34j089efj0defsj320rue0fjdpsm322 vs 34nmfd9834klondrfskadlofdn98wj34
    - Dump 2, OK
    - Dump 3, OK
    
    Verified Games:
    - Dump 2
    - Dump 3

    Games Unknown By Name:
    - Dump 4

    Games With Errors:
    - Dump 1
       * Error on file Dump 1.cue - md5 missmatch: n34j089efj0defsj320rue0fjdpsm322 vs 34nmfd9834klondrfskadlofdn98wj34
       * Dump 1 (Track 1).bin - OK
       * Dump 1 (Track 2).bin - OK

The logfile "redump-check.log" will be created, it contains a more detailed listing of the checked files:

    2022-05-02 17:45:31       ~~~~~~~~~~ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ~~~~~~~~~~ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
    2022-05-02 17:45:31       INFO       CONFIG                                        NONE       Dat File: D:\Sony - PlayStation - Datfile (10649) (2022-05-02 09-44-32).dat
    2022-05-02 17:45:31       INFO       CONFIG                                        NONE       ROM Folder: D:\path\to\collection 
    2022-05-02 17:45:31       INFO       CONFIG                                        NONE       Allowed Extensions: .cue, .bin 
    2022-05-02 17:45:31       INFO       CONFIG                                        NONE       Recursive: Yes 
    2022-05-02 17:45:31       INFO       Dump 1                                        LOCATION   D:\path\to\collection\Dump1 
    2022-05-02 17:46:05       INFO       Dump 1                                        ROM        Dump 1 (Track 1).bin - OK 
    2022-05-02 17:46:08       INFO       Dump 1                                        ROM        Dump 1 (Track 2).bin - OK 
    2022-05-02 17:46:08       INFO       Dump 1                                        GAME       Dump 1 - Had errors, see errorlog 
    2022-05-02 17:46:08       INFO       Dump 2                                        LOCATION   D:\path\to\collection\Dump2
    2022-05-02 17:46:08       INFO       Dump 2                                        ROM        Dump 2.cue - OK 
    2022-05-02 17:46:48       INFO       Dump 2                                        ROM        Dump 2.bin - OK 
    2022-05-02 17:46:48       INFO       Dump 2                                        GAME       All checks ok 
    2022-05-02 17:46:48       INFO       Dump 3                                        LOCATION   D:\path\to\collection\Dump3
    2022-05-02 17:46:48       INFO       Dump 3                                        ROM        Dump 3.cue - OK 
    2022-05-02 17:47:13       INFO       Dump 3                                        ROM        Dump 3.bin - OK 
    2022-05-02 17:47:14       INFO       Dump 3                                        GAME       All checks ok
    2022-05-02 17:47:17       INFO       Dump 4                                        GAME       Unknown Game, it was not found in the provided datfile 

If errors occure, the errorlog "redump-check.err" will be writen

    2022-05-02 17:45:33       ERROR      Dump 1                                        ROM        file Dump 1.cue - md5 missmatch: n34j089efj0defsj320rue0fjdpsm322 vs 34nmfd9834klondrfskadlofdn98wj34 
    2022-05-02 17:46:08       ERROR      Dump 1                                        GAME       Had errors 
    2022-05-02 17:47:17       ERROR      Dump 4                                        GAME       Unknown Game, it was not found in the provided datfile 

# Todo

Reverse searching for unknown games, using the hash of its files.
