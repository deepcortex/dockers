dockers = %x[git diff --name-only $TRAVIS_COMMIT_RANGE].split("\n").select{ |f| f[/[\w-]*\/.*/] }.map { |f| f[/[\w-]*/] }.uniq

puts dockers