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
  argp.add_argument("-d", "--dedupe", required=False, nargs="?", type=argparse.FileType("r"), default="-", help="Path to lines of MAINNICK ALIAS1 ALIAS2 ...")
  args = argp.parse_args()

  dedupe = {}
  #dedupe_path = args.in_json_directory + "/dedupe.txt"
  if args.dedupe:
    print "Dedupes:"
    for l in args.dedupe:
      nicks = l.rstrip('\n').split(" ")
      print "  ", nicks[0], "<--", nicks[1:]
      if len(nicks) > 0:
        for nick in nicks[1:]:
          dedupe[nick] = nicks[0]

  player_message_totals = {}
  player_message_counts = {}
  player_message_activity = {}
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
      deduped_nick = nick
      if nick in dedupe:
        deduped_nick = dedupe[nick]

      if deduped_nick not in player_message_totals:
        player_message_totals[deduped_nick] = 0
      if deduped_nick not in player_message_activity:
        player_message_activity[deduped_nick] = 0
      if deduped_nick not in player_message_counts:
        player_message_counts[deduped_nick] = {}
      if yyyy_mm_dd not in player_message_counts[deduped_nick]:
        player_message_counts[deduped_nick][yyyy_mm_dd] = 0
      player_message_counts[deduped_nick][yyyy_mm_dd] += message_counts["message_counts"][nick]
      player_message_totals[deduped_nick] += message_counts["message_counts"][nick]

  args.out_json.write(json.dumps({
    "player_message_totals": player_message_totals,
    "player_message_counts": player_message_counts,
    "all_yyyy_mm_dd": sorted(all_yyyy_mm_dd)
  }, indent=2))
