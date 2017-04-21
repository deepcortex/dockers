#!/usr/bin/env ruby

def exclusion
  %w[ scripts ]
end

def print_env
  puts "TRAVIS_BRANCH: #{ENV['TRAVIS_BRANCH']}"
  puts "TRAVIS_TAG: #{ENV['TRAVIS_TAG']}"
  puts "TRAVIS_PULL_REQUEST: #{ENV['TRAVIS_PULL_REQUEST']}"
  puts "TRAVIS_COMMIT_RANGE #{ENV['TRAVIS_COMMIT_RANGE']}"
end

def changes
  all = %x[git diff --name-only $TRAVIS_COMMIT_RANGE].split("\n")
  all.select { |path| path[/[\w-]*\/.*/] }
end

print_env
puts "exclusion: #{exclusion}"
puts "changes: #{changes}"

all_folders = changes.map { |f| f[/[\w-]*/] }.uniq
puts "all_folders: #{all_folders}"

dockers_to_build = all_folders - exclusion
puts "dockers_to_build: #{dockers_to_build}"

dockers_to_build.each do |docker|
  puts docker
end.empty? and begin
  puts 'Nothing to build'
end