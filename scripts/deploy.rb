#!/usr/bin/env ruby

def exclusion
  %w[ scripts ]
end

def changes
  all = %x[git diff --name-only $TRAVIS_COMMIT_RANGE].split("\n")
  all.select { |path| path[/[\w-]*\/.*/] }
end

all_folders = changes.map { |f| f[/[\w-]*/] }.uniq

dockers_to_deploy = all_folders - exclusion

dockers_to_deploy.each do |docker|
  %x[cd $docker && make push]
end.empty? and begin
  puts 'Nothing to deploy'
end