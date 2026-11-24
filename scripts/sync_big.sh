#!/bin/bash
remote="n@nd"
src="/home/n/Repos/retail-bot/"
dst="/home/n/Repos/retail-bot/"
ssh "$remote" "cd '$src' && git ls-files -z --others" \
  | rsync -av --from0 --files-from=- "$remote:$src/" "$dst/"

