#!/usr/bin/env ruby

require_relative 'utils.rb'

print_env
puts "exclusion: #{exclusion}"
puts "changes: #{changes}"
puts "all_folders: #{all_folders}"
puts "dockers_to_build: #{dockers_to_build}"

dockers_to_build.each do |docker|
  puts "Building #{docker} image..."
  output = %x[cd #{docker} && make pre-release]
  puts output
  puts "#{docker}... image has been built"
end.empty? and begin
  puts 'Nothing to build'
end