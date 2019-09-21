# quipdiff

Get diff from quip ★ starred ★ documents, or specify documents and folders.

## Screenshots

### Mutt (with highlighting)

![mutt](https://raw.githubusercontent.com/torvald/quipdiff/master/screenshots/mutt.png)

With colors of you choosing to go in `.muttrc`.

 ```
 # colorfull diffs in email
 color body green default "^diff \-.*"
 color body green default "^index [a-f0-9].*"
 color body green default "^\-\-\- .*"
 color body green default "^[\+]{3} .*"
 color body cyan default "^[\+][^\+]+.*"
 color body red  default "^\-[^\-]+.*"
 color body brightblue default "^@@ .*"
 ```

### GMail (with HTML colors)

![gmail](https://raw.githubusercontent.com/torvald/quipdiff/master/screenshots/gmail.png)

## Set up
 
 ```
 git clone git@github.com:torvald/quipdiff.git
 git clone https://github.com/quip/quip-api.git
 cd quipdiff
 ln -s ../quip-api/python/quip.py quip.py
 cp config.py.example config.py
 vim config.py
 ```

Test the it with

  `python quipdiff.py`

And add it to cron on a terminal server near you for profit

  `0 * * * * python /home/badguy90/dev/quipdiff/quipdiff.py`

## TODO

 * Better error handling
 * Convert documents to markdown or something instead of just plain text.
 * Add support for recursively traversing folders
