I'm sitting in Elmhurst on UP-W train #38 at 9:05 a.m. on a
Tuesday.

I've got a meeting at 9:45 in the loop.

Will I make it on time?

[cue Blues Brother's theme music]

marey-metra
===========

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

developing
==========

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
   sudo pip install -r REQUIREMENTS
   ```

