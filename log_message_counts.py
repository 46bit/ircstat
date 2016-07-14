#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

'''
HOW TO USE
for file in znc-logs/\#cs-york/*.log
do
  python log_message_counts.py -i "${file}" -o "${file}.json"
done

PROCESS
.log -> .json
{
  "message_counts": {
    "_46bit": 125,
    ...
  }
}

RECOGNISED MESSAGE PATTERNS
[HH:MM:SS] <NICK> MESSAGETEXT
[HH:MM:SS] * NICK MESSAGETEXT
'''

def parse_log_entry(line):
  time_parse = re.match("\[([0-9]{2}):([0-9]{2}):([0-9]{2})\] (.*)$", line)
  if time_parse is None: return False
  time_parse = time_parse.groups()
  hh_mm_ss = time_parse[0:3]

  rest = time_parse[3]

  msg_parse = re.match("<([^>]+)> (.*)$", rest)
  if msg_parse is not None:
    msg_parse = msg_parse.groups()
    return {
      "nick": msg_parse[0],
      "text": msg_parse[1],
      "type": "msg"
    }

  me_parse = re.match("\* ([^ ]+) (.*)$", rest)
  if me_parse is not None:
    me_parse = me_parse.groups()
    return {
      "nick": me_parse[0],
      "text": me_parse[1],
      "type": "me"
    }

  notice_parse = re.match("-([^ ]+)- (.*)$", rest)
  if notice_parse is not None:
    notice_parse = notice_parse.groups()
    return {
      "nick": notice_parse[0],
      "text": notice_parse[1],
      "type": "notice"
    }

  return False

if __name__ == "__main__":
  import os, sys, argparse, re, json

  argp = argparse.ArgumentParser(description="")
  argp.add_argument("-i", "--in_log", nargs="?", type=argparse.FileType("r"), default="-", help="Path to input .log file.")
  argp.add_argument("-o", "--out_json", nargs="?", type=argparse.FileType("w"), default="-", help="Path to out .json summary file.")
  args = argp.parse_args()

  message_counts = {}

  for line in args.in_log:
    entry = parse_log_entry(line)
    if entry is False: continue
    if entry["nick"] not in message_counts:
      message_counts[entry["nick"]] = 0
    message_counts[entry["nick"]] += 1

  args.out_json.write(json.dumps({
    "message_counts": message_counts
  }, indent=2))
