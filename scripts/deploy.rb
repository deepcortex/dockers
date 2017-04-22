#!/usr/bin/env ruby

require_relative 'utils.rb'

dockers_to_build.each do |docker|
  puts "Deploying #{docker} image..."
  %x[cd #{docker} && make push]
  puts "#{docker}... image has been deployed"
end.empty? and begin
  puts 'Nothing to deploy'
end