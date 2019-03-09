# quipdiff

 Get diff from quip documents you follow 

## Set up

  git clone git@github.com:torvald/quipdiff.git
  git clone https://github.com/quip/quip-api.git
  cd quipdiff
  ln -s ../quip-api/python/quip.py quip.py
  cp config.py.example config.py 
  vim config.py

Test the it with

  python quipdiff.py

And add it to cron on a terminal server near you for profit

  0 * * * * python /home/badguy90/dev/quipdiff/quipdiff.py

## TODO

 * Better error handeling
