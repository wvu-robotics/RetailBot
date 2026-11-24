WORKTREE := setup_testing/tmp/retail-bot

prepare:
	if [ ! -d tmp/retail-bot ]; then \
		git -C .. worktree add --force --detach setup_testing/tmp/retail-bot; \
	# else \
	# 	cd tmp/retail-bot && git fetch origin && git reset --hard HEAD && git submodule update --init --recursive; \
	fi

run: prepare
	vagrant up --provider=virtualbox --provision

reload: prepare
	vagrant rsync
	vagrant up --provider=virtualbox --provision
