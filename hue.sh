#!/bin/bash

command="curl -s -H \"Content-Type: application/json\" http://hostname/api/key"
function show_usage {
  echo $"Usage: $0 {off | prealarm | day | evening | bedtime}"
  echo $"       $0 { on ct bri }"
  echo "    use - to omit paramaters"
  exit 1
}

if [ "$#" -eq 3 ]; then
  data="{"
  if [[ ! "$1" = "-"  ]]; then
    data="$data \"on\": $1"
#  else show_usage
  fi
  if [[ ! $2 = "-" ]]; then
      if [[ ! "$data" = "{"  ]]; then
        data="$data,"
      fi
      data="$data \"ct\": $2"
  fi
  if [[ ! $3 = "-" ]]; then
    if [[ ! "$data" = "{" ]]; then
      data="$data,"
    fi
    data="$data \"bri\": $3"
  fi
  data="$data }"
elif [ "$#" -eq 1 ]; then
  case "$1" in
    prealarm)
      data='{"on": true, "ct": 180, "bri": 1}'
      ;;

    bedtime)
      data='{"on": true, "ct": 450, "bri": 10}'
      ;;

    day)
      data='{"on": true, "ct": 180, "bri": 254}'
      ;;

    evening)
      data='{"on": true, "ct": 294, "bri": 200}'
      ;;

    off)
      data='{"on": false}'
      ;;

    *)
      show_usage
  esac
elif [[ "$#" -eq 0  ]]; then
  show_usage
fi
#echo $data
$command/groups/1/action -X PUT -d "$data" | json_pp
