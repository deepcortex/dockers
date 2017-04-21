#!/usr/bin/env ruby

require 'utils.rb'

dockers_to_build.each do |docker|
  %x[cd $docker && make push]
end.empty? and begin
  puts 'Nothing to deploy'
end