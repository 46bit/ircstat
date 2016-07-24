#!/usr/bin/env zsh

log_directory=${argv[1]}
print "Running in log directory:\n  ${log_directory}"
for channel in "${log_directory}"/*
do
  if [ ! -d "$channel" ]; then
    continue
  fi

  channelname=$(basename "${channel/\#/}")
  print "${channel} ${channelname}"

  echo -n "  "
  for log in "${channel}"/*.log
  do
    echo -n "."
    python2 log_message_counts.py -i "${log}" -o "${log}.json"
  done
  print

  player_message_counts="${channel}/player_message_counts.json"
  python2 nick_message_counts.py -i "${channel}" -o "${player_message_counts}" -d "${log_directory}/dedupe.txt"

  cp "${player_message_counts}" "webroot/${channelname}.json"
  cp "webroot/_channel_info.html" "webroot/${channelname}.html"
done
