znc-inbox
=========

A ZNC plugin to keep a list of mentions of your nick or other keywords.

##Installation
Make sure you have python3-dev installed and your [ZNC is compiled with Python support](http://wiki.znc.in/Modpython#Compiling). 

##Usage
By default the module will watch for mentions of your nick. To see the last 5 times your nick was mentionned, type `/msg *inbox show 5`. Use `show-v` for a more detailed output. If you want the module to watch out for other keywords as well, use `add-trigger`. For example: `/msg *inbox add-trigger foo` adds foo to the list of words to watch out for. `/msg *inbox remove-trigger foo` will remove it from this list.
