I'm sitting in Elmhurst on UP-W train #38 at 9:05 a.m. on a
Tuesday.

I've got a meeting at 9:45 in the loop.

I wonder, *will I make it on time?*

{{ cue [Peter Gunn Theme](https://www.youtube.com/watch?v=oysMt8iL9UE&feature=kp) }}

back story
==========

The goal of this project is to make it easy for Metra riders (and
especially myself, because I seem to always be cutting it close) to
determine whether they are going to be on time. This works by
periodically pulling data from Metra's
[Rail Time Tracker](https://metrarail.com/metra/wap/en/home/RailTimeTracker.html)
to determine the historical record of on-time performance and using it
to estimate when you are likely to arrive at your destination.

The data visualization takes inspiration from
[Marey](http://en.wikipedia.org/wiki/%C3%89tienne-Jules_Marey)'s train
visualizations from Paris to Lyon in his book
[La Méthode Graphique](https://archive.org/details/lamthodegraphiq00maregoog):

![train lines](http://i.imgur.com/8bQOM8F.jpg "Train lines visualized by Marey")

The idea is that these simple lines can show you how likely you are to
"make up time" and possibly make your meeting.

I was
[originally hesitant](https://twitter.com/deanmalmgren/status/455709231614681088)
to download this information in this way and I tried to obtain this
information by
[a FOIA request on 2014 April 17](https://docs.google.com/document/d/1oyaIARPyksTUERpBNvef9PU_6XgC3keSUk9LmqrEBBc/edit?usp=sharing). Unfortunately,
[Metra only maintains arrival / departure records for 30 days](https://drive.google.com/file/d/0ByojUCBHn7gJT1JvTGhKOWNaa1k/view?usp=sharing),
which isn't going to provide the kinds of statistics and up-to-date
information I'd like to have. For example, if construction starts or
stops on a particular line, I'd like those delays to be incorporated
into my estimated arrival. As a result, I've resorted to the original
idea of just scraping the Rail Time Tracker system in a relatively
polite way with the hopes that I can subsequently make this data
available to others, possibly via the
[Chicago Data Portal](https://data.cityofchicago.org/) or a
[Fusion Table](https://support.google.com/fusiontables/answer/2571232).

want to contribute?
===================

1. Clone this repository

2. Install virtualenvwrapper and make sure to [properly setup your ~/.bashrc](http://virtualenvwrapper.readthedocs.org/en/latest/install.html#shell-startup-file)

   ```bash
   sudo pip install virtualenvwrapper
   ```

   ```bash
   # add this to the end of your ~/.bashrc
   WORKON_HOME=~/.virtualenvs
   mkdir -p ${WORKON_HOME}
   vew=/usr/local/bin/virtualenvwrapper.sh
   if [ -e ${vew} ]; then
       source ${vew}
   fi
   ```
   Then source your ```.bashrc``` file.

3. Create a python virtualenv in OSX and install all the necessary
   packages for provisioning / deploying with fabric:

   ```bash
   mkvirtualenv marey-metra
   pip install -r REQUIREMENTS
   ```
