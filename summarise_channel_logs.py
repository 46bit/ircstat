#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

'''
Should work under Python 2.7+ and Python 3.

USAGE:
  python summarise_channel_logs.py -i ../path/to/logs/of/#cs-york -o cs-york-summary.json
'''

import os, sys, argparse, re, json
from collections import namedtuple, defaultdict

LogItem = namedtuple("LogItem", ["type", "nick", "text"])

# Parse a line of the logs.
def parse_log_line(line):
  # TIMESTAMP
  # Recognise pattern like
  #   [YYYY-MM-DD] REST_OF_LINE
  time_parse = re.match("\[([0-9]{2}):([0-9]{2}):([0-9]{2})\] (.*)$", line)
  if time_parse is None: return False
  time_parse = time_parse.groups()
  hh_mm_ss = time_parse[0:3]
  # Now to parse REST_OF_LINE
  rest = time_parse[3]

  # MESSAGE
  # Recognise patterns after timestamp like
  #   <NICK> MESSAGETEXT
  msg_parse = re.match("<([^>]+)> (.*)$", rest)
  if msg_parse is not None:
    msg_parse = msg_parse.groups()
    return LogItem(type="privmsg", nick=msg_parse[0], text=msg_parse[1])

  # ACTION
  # Recognise patterns after timestamp like
  #   * NICK MESSAGETEXT
  action_parse = re.match("\* ([^ ]+) (.*)$", rest)
  if action_parse is not None:
    action_parse = action_parse.groups()
    return LogItem(type="action", nick=action_parse[0], text=action_parse[1])

  # NOTICE
  # Recognise patterns after timestamp like
  #  -NICK- MESSAGETEXT
  notice_parse = re.match("-([^ ]+)- (.*)$", rest)
  if notice_parse is not None:
    notice_parse = notice_parse.groups()
    return LogItem(type="action", nick=notice_parse[0], text=notice_parse[1])

  return False

if __name__ == "__main__":
  argp = argparse.ArgumentParser(description="")
  argp.add_argument("-i", "--channel_log_dir", help="Path to directory of input .log files.")
  argp.add_argument("-o", "--summary_json_out", nargs="?", type=argparse.FileType("w"), default="-", help="Path to out .json summary file.")
  argp.add_argument("-d", "--dedupe_file", required=False, nargs="?", type=argparse.FileType("r"), help="Path to lines of MAINNICK ALIAS1 ALIAS2 ...")
  args = argp.parse_args()

  # Parse -d|--dedupe_file dedupe file if provided.
  dedupe = {}
  if args.dedupe_file:
    sys.stderr.write("Dedupes:\n")
    for l in args.dedupe_file:
      nicks = l.rstrip('\n').split(" ")
      sys.stderr.write("  %s <-- %s\n" % (nicks[0], nicks[1:]))
      if len(nicks) > 0:
        for nick in nicks[1:]:
          dedupe[nick] = nicks[0]
    sys.stderr.flush()

  # messages_all_time[NICK] is an int
  messages_all_time = defaultdict(int)
  # messages_by_day[DATE][NICK] is an int
  messages_by_day = defaultdict(lambda: defaultdict(int))

  # Get a list of YYYY-MM-DD.log files in the -i|--channel_log_dir directory.
  files = os.listdir(args.channel_log_dir)
  logfiles = [filename for filename in files if filename.endswith(".log")]
  logfiles = sorted(logfiles)

  # Find the earliest and latest logs.
  if len(logfiles) > 0:
    earliest_date = logfiles[0].replace(".log", "")
    latest_date = logfiles[-1].replace(".log", "")
  else:
    earliest_date = latest_date = None

  # Count messages by nick in all logfiles.
  for logfile in logfiles:
    sys.stderr.write(".")
    sys.stderr.flush()

    # Recognise patterns like
    #  YYYY-MM-DD
    # in YYYY-MM-DD.log
    date_match = re.match("([0-9]{4}-[0-9]{2}-[0-9]{2})", logfile)
    if date_match is None:
      continue
    date = date_match.groups()[0]

    f = open(args.channel_log_dir + "/" + logfile, "rb")
    log_text = f.read().decode('utf8', errors='ignore') #unicode(f.read(), errors='ignore')
    f.close()

    for log_line in log_text.splitlines():
      log_item = parse_log_line(log_line)
      if not log_item:
        continue

      deduped_nick = dedupe[log_item.nick] if log_item.nick in dedupe else log_item.nick

      messages_all_time[deduped_nick] += 1
      messages_by_day[date][deduped_nick] += 1
  sys.stderr.write("\n")

  drop_nicks = []
  for nick in messages_all_time:
    if messages_all_time[nick] < 30:
      drop_nicks.append(nick)
  for drop_nick in drop_nicks:
    del messages_all_time[drop_nick]
    for date in messages_by_day:
      if drop_nick in messages_by_day[date]:
        del messages_by_day[date][drop_nick]

  # Output to -o|--summary_json_out JSON file.
  args.summary_json_out.write(json.dumps({
    "earliest_date": earliest_date,
    "latest_date": latest_date,
    "messages_all_time": messages_all_time,
    "messages_by_day": messages_by_day
  }, indent=2))
