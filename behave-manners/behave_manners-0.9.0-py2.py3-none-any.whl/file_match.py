
'''
Glob	Description
*.txt	Matches all files that has extension as txt.
*.{html,htm}	Matches all files that has extension as html or htm. { } are used to group patterns and , comma is used to separate patterns.
?.txt	Matches all files that has any single charcter as name and extension as txt.
*.*	Matches all files that has . in its name.
C:\\Users\\*	Matches any files in C: 'Users' directory in Windows file system. Backslash is used to escape a special character.
/home/**	Matches /home/foo and /home/foo/bar on UNIX platforms. ** matches strings of characters corssing directory boundaries.
[xyz].txt	Matches a file name with single character 'x' or 'y' or 'z' and extension as txt. Square brackets [ ] are used to sepcify a character set.
[a-c].txt	Matches a file name with single character 'a' or 'b' or 'c' and extension as txt. Hypehen - is used to specify a range and used in [ ]
[!a].txt	Matches a file name with single character that is not 'a'. ! is used for negation.
'''
