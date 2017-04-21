#!/usr/bin/env ruby

require_relative 'utils.rb'

print_env
puts "exclusion: #{exclusion}"
puts "changes: #{changes}"
puts "all_folders: #{all_folders}"
puts "dockers_to_build: #{dockers_to_build}"

dockers_to_build.each do |docker|
  %x[cd $docker && make build]
end.empty? and begin
  puts 'Nothing to build'
end