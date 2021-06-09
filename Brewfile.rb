cask_args appdir: "/Applications"

tap "getsentry/tools"
tap "heroku/brew"
tap "homebrew/bundle"
tap "homebrew/cask"
tap "homebrew/core"
tap "homebrew/services"

brew "python@3.9"
brew "git"
brew "mailhog", restart_service: true
brew "pipenv"
brew "postgresql", restart_service: true
brew "redis", restart_service: true
brew "watchman"
brew "getsentry/tools/sentry-cli"
brew "heroku/brew/heroku"

cask "github"
cask "sublime-text"
cask "sublime-merge"
cask "tableplus"
