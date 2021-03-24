get_git_log:
	git -C $(path) log --pretty=format:"%n%an" --name-only --reverse > ./logs/$(name)_git_log_output.txt

