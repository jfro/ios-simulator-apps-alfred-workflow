#!/bin/env ruby
xcodes = Dir.glob("/Applications/Xcode*.app")
puts xcodes
xcodes.each do |xcode|
	if File.exist? "#{xcode}/Contents/Developer/usr/bin/xcrun"
		simctl = "#{xcode}/Contents/Developer/usr/bin/xcrun simctl"
	else
		simctl = "#{xcode}/Contents/Developer/usr/bin/simctl"
	end
	puts "#{simctl} list"
	out = %x{#{simctl} list}
	out.lines.each do |line|
		match = /(\s+)(.*)\s\(([\d\w]{8}-[\w\d]{4}-[\w\d]{4}-[\w\d]{4}-[\w\d]{12})\)/.match(line)
		if match
			id = match[3]
			name = match[2]
			puts "Erasing #{name} (#{id})"
			result = system("#{simctl} erase #{id}")
			if not result
				puts "Failed to erase #{name} - #{id}"
			end
		end
	end
end
