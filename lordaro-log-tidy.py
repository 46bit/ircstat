#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

'''
Should work under Python 2.7+ and Python 3.

USAGE:
  python summarise_channel_logs.py -i ../path/to/logs/of/#cs-york -o cs-york-summary.json
'''

import os, sys, argparse, re, json, time
from collections import namedtuple, defaultdict

LogItem = namedtuple("LogItem", ["day", "month", "year", "hour", "minute", "second", "type", "nick", "text"])

# Parse a line of the logs.
def parse_log_line(line, latest_year):
  year_parse = re.match("~~~ ([0-9]{4})$", line)
  if year_parse is not None:
      return int(year_parse.groups()[0])

  # TIMESTAMP
  # Recognise pattern like
  #   MON DD HH:MM:SS
  time_parse = re.match("([a-zA-Z]{3})\s([0-9]{2})\s([0-9]{2}):([0-9]{2}):([0-9]{2})\s+(.*)$", line)
  if time_parse is None: return False
  time_parse = time_parse.groups()
  month = time_parse[0]
  mm = time.strptime(month, "%b").tm_mon
  dd = time_parse[1]
  hh_mm_ss = time_parse[2:5]
  # Now to parse REST_OF_LINE
  rest = time_parse[5]

  # MESSAGE
  # Recognise patterns after timestamp like
  #   <NICK> MESSAGETEXT
  msg_parse = re.match("<\s*([^>]+)\s*>\s+(.*)$", rest)
  if msg_parse is not None:
    msg_parse = msg_parse.groups()
    return LogItem(day=int(dd), month=int(mm), year=latest_year, hour=int(hh_mm_ss[0]), minute=int(hh_mm_ss[1]), second=int(hh_mm_ss[2]), type="privmsg", nick=msg_parse[0], text=msg_parse[1])

  # ACTION
  # Recognise patterns after timestamp like
  #   * NICK MESSAGETEXT
  action_parse = re.match("\*\s+([^ ]+)\s+(.*)$", rest)
  if action_parse is not None:
    action_parse = action_parse.groups()
    return LogItem(day=int(dd), month=int(mm), year=latest_year, hour=int(hh_mm_ss[0]), minute=int(hh_mm_ss[1]), second=int(hh_mm_ss[2]), type="action", nick=action_parse[0], text=action_parse[1])

  # NOTICE
  # Recognise patterns after timestamp like
  #  -NICK- MESSAGETEXT
  notice_parse = re.match("-\s*([^ ]+)-\s+(.*)$", rest)
  if notice_parse is not None:
    notice_parse = notice_parse.groups()
    return LogItem(day=int(dd), month=int(mm), year=latest_year, hour=int(hh_mm_ss[0]), minute=int(hh_mm_ss[1]), second=int(hh_mm_ss[2]), type="action", nick=notice_parse[0], text=notice_parse[1])

  return False

if __name__ == "__main__":
  argp = argparse.ArgumentParser(description="")
  argp.add_argument("-i", "--lordaro_log_in", nargs="?", type=argparse.FileType("r"), default="-", help="Path to input logaro log file.")
  argp.add_argument("-o", "--converted_logs_out", help="Directory path for output .log files.")
  argp.add_argument("-d", "--dedupe_file", required=False, nargs="?", type=argparse.FileType("r"), help="Path to lines of MAINNICK ALIAS1 ALIAS2 ...")
  args = argp.parse_args()

  # Parse -d|--dedupe_file dedupe file if provided.
  dedupe = {}
  if args.dedupe_file:
    print("Dedupes:")
    for l in args.dedupe_file:
      nicks = l.rstrip('\n').split(" ")
      print("  ", nicks[0], "<--", nicks[1:])
      if len(nicks) > 0:
        for nick in nicks[1:]:
          dedupe[nick] = nicks[0]

  # messages_by_day[DATE][NICK] is an int
  messages_by_day = defaultdict(list)

  latest_year = None
  log_text = args.lordaro_log_in.read()
  for log_line in log_text.splitlines():
    log_item = parse_log_line(log_line, latest_year)
    #print(log_item)
    if not log_item:
      continue

    if type(log_item) is int:
        latest_year = log_item
    else:
        #[20:42:47] * Now talking on #cs-york
        if log_item.text.startswith("Now talking on #cs-york"): continue
        #[20:42:47] * Topic for #cs-york is: An unofficial place for people studying or interested in computer science at the UniOfYork :: Chat bot code: http://git.io/csyork Discussion: #cs-york-dev :: Study Group Poll: http://bit.ly/17Jl2qj
        #[20:42:47] * Topic for #cs-york set by barrucadu!~barrucadu@fsf/member/barrucadu at Sat Oct  5 23:33:52 2013
        if log_item.nick == "Topic": continue
        if log_item.nick == "Now": continue
        #[20:42:47] * ChanServ [#cs-york] Welcome to the #cs-york IRC channel, an unofficial place for people studying or interested in computer science at the University of York in the UK to hang out and chat.
        if log_item.nick == "ChanServ": continue
        #[20:42:47] * #cs-york :http://hacksoc.org
        if log_item.nick == "#cs-york": continue
        # [14:13:34] <***> Buffer Playback...
        if log_item.nick == "***": continue

        #print(log_item)
        date = "%04d-%02d-%02d" % (log_item.year, log_item.month, log_item.day)
        messages_by_day[date].append(log_item)
  print(sum([len(messages_by_day[k]) for k in messages_by_day]))

  for date in messages_by_day:
    logfilename = "%s/%s.log" % (args.converted_logs_out, date)
    log = ""
    for log_item in messages_by_day[date]:
      if log_item.type == "privmsg":
        log += "[%02d:%02d:%02d] <%s> %s\n" % (log_item.hour, log_item.minute, log_item.second, log_item.nick, log_item.text)
      elif log_item.type == "action":
        log += "[%02d:%02d:%02d] * %s %s\n" % (log_item.hour, log_item.minute, log_item.second, log_item.nick, log_item.text)

    with open(logfilename, "w+") as f:
      f.write(log)
