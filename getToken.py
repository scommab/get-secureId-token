#!/usr/bin/env python

import os
import sys
import getopt
from getpass import getpass
# this script modified from
# http://coreygilmore.com/projects/automated-securid-token-generation-and-vpn-login-applescript/
script = """osascript <<-EOF

-- launch the SecurID application and retrieve the current token
on get_token(userPin, tokenAppName)
  set theToken to null
  
  -- quit the app if it's running
  tell application "System Events" to set allApps to (get name of every application process)
  
  if allApps contains tokenAppName then
    tell application tokenAppName to quit
    log "telling " & tokenAppName & " to quit"
    delay 0.5 -- arbitrary delay, give the app time to exit
  end if
  
  tell application tokenAppName
    activate
    copy (get the clipboard) to origClip
    tell application "System Events"
      delay 0.2
      keystroke userPin
      key code 36
      repeat with x from 1 to 20
        delay 0.1
        keystroke "c" using command down
        keystroke "c" using command down -- copy twice because it didn't always work the first time
        delay 0.1
        copy (get the clipboard) to theToken
        if theToken is origClip then -- if the clipboard hasn't changed, the token hasn't been generated (edge case: clipboard at launch matches the generated token)
          -- do nothing
        else
          log "Token is: " & theToken
          --keystroke "q" using command down
          set the clipboard to origClip -- reset the clipboard to what it was before
          --return (theToken as string) -- return the token we retrieved
          exit repeat
        end if
      end repeat
    end tell
  end tell
  tell application tokenAppName to quit
  log theToken
  return (theToken as string) -- return the token we retrieved
end get_token

set Pin to "%s"
set appName to "SecurID"
--set the clipboard to get_token(Pin, appName)
%s get_token(Pin, appName)
EOF"""

def print_help():
  print """
  getToken.py - a command line tool to get your RSA token

    -h --help       This screen
    -p --pin        Set the pin to use
    -c --clipboard  put the token in your clipboard as well as print it

    You can also save your pin to ~/.rsa/pin which is convenient, but not
    secure
  """

opts, args = getopt.getopt(sys.argv[1:], "hcp:", ["clipboard", "help", "pin="])
pin = ""
clipboard = ""
for o, a in opts:
  if o in ("-h", "--help"):
    print_help()
    sys.exit()
  elif o in ("-p", "--pin"):
    pin = a
  elif o in ("-c", "--clipboard"):
    clipboard = "set the clipboard to "
  else:
    raise Exception("Unknown option, use --help for details")
# FYI: using the pin file isn't secure, but it is convenient
pin_file = os.path.expanduser("~/.rsa/pin")
if pin:
  pass # we setup pin as a param
elif os.path.exists(pin_file):
  pin = open(pin_file).readlines()[0].strip()
else:
  pin = getpass("RSA Pin: ")
c = script % (pin, clipboard)
os.popen(c)
