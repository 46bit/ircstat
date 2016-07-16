#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

'''
HOW TO USE
python nick_message_counts.py -i "znc-logs/#cs-york" -o "znc-logs/#cs-york/player_message_counts.json"

PROCESS
log_message_counts.json -> nick_message_counts.json
{
  "message_counts": {
    "_46bit": 125,
    ...
  }
}
'''

if __name__ == "__main__":
  import os, sys, argparse, re, json

  argp = argparse.ArgumentParser(description="")
  argp.add_argument("-i", "--in_json_directory", help="Path to directory of input .json files.")
  argp.add_argument("-o", "--out_json", nargs="?", type=argparse.FileType("w"), default="-", help="Path to out .json summary file.")
  args = argp.parse_args()

  player_message_totals = {}
  player_message_counts = {}
  all_yyyy_mm_dd = []
  dirlist = os.listdir(args.in_json_directory)
  for filepath in sorted(dirlist, reverse=True):
    if not filepath.endswith(".log.json"):
      continue

    yyyy_mm_dd = re.match("^[.+/]?([^\./]*)", filepath).groups()[0]
    all_yyyy_mm_dd.append(yyyy_mm_dd)

    f = open(args.in_json_directory + "/" + filepath)
    message_counts_json = unicode(f.read(), errors='ignore')
    f.close()

    message_counts = json.loads(message_counts_json)
    for nick in message_counts["message_counts"]:
      if nick not in player_message_totals:
        player_message_totals[nick] = 0
      if nick not in player_message_counts:
        player_message_counts[nick] = {}
      if yyyy_mm_dd not in player_message_counts[nick]:
        player_message_counts[nick][yyyy_mm_dd] = 0
      player_message_counts[nick][yyyy_mm_dd] += message_counts["message_counts"][nick]
      player_message_totals[nick] += message_counts["message_counts"][nick]

  args.out_json.write(json.dumps({
    "player_message_totals": player_message_totals,
    "player_message_counts": player_message_counts,
    "all_yyyy_mm_dd": sorted(all_yyyy_mm_dd)
  }, indent=2))
