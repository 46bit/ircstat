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

  player_message_counts="${channel}/player_message_counts.json"
  pypy3 summarise_channel_logs.py -i "${channel}" -d "${log_directory}/dedupe.txt" -o "${player_message_counts}"

  cp "${player_message_counts}" "webroot/${channelname}.json"
  cp "webroot/_channel_info.html" "webroot/${channelname}.html"
done

#python3 political_compass.py -i ../znc-logs/freenode/\#cs-york -d ../znc-logs/freenode/dedupe.txt -o webroot/cs-york-pc-political-compass.json
