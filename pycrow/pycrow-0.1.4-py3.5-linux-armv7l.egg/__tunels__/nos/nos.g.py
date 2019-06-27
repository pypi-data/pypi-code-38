import licant

licant.module("nos.util",
	srcdir="nos/util", 
	sources=[
		"trace.cpp",
		"osutil.cpp",
	],
	mdepends=["igris.util"]
)

licant.module("nos.io",
	srcdir="nos/io", 
	sources=[
		"ostream.cpp"
	],
	mdepends=["nos.current_ostream"]
)

licant.module("nos.inet",
	srcdir="nos/inet", 
	sources=[
		"common.cpp",
		"tcp_server.cpp",
		"tcp_socket.cpp"
	],
	mdepends=["nos.current_ostream"]
)

licant.module("nos.print",
	srcdir="nos/print", 
	sources=[
		"print.cpp",
		"stdtype.cpp",
	],
	mdepends=["nos.current_ostream"]
)

licant.module("nos.input",
	srcdir="nos/input", 
	sources=[
		"input.cpp",
	],
	mdepends = ["nos.util"]
)

licant.module("nos.fprint",
	srcdir="nos/fprint", 
	sources=[
		"fprint.cpp",
		"stdtype.cpp",
	],
	mdepends=["nos.current_ostream"]
)

licant.module("nos.current_ostream", impl="stdout", 
	sources=["nos/io/current_ostream_stdout.cpp", "nos/io/stdfile.cpp"],
	mdepends = ["nos.io"],
	default = True
)

licant.module("nos.current_ostream", impl="nullptr", 
	sources=["nos/io/current_ostream_nullptr.cpp"],
	mdepends = ["nos.io"]
)


#licant.module("nos.printf", sources=["nos/util/printf_impl.c"])

licant.module("nos.error", impl="throw", sources=["nos/util/error_throw.cpp"])
licant.module("nos.error", impl="abort", sources=["nos/util/error_abort.cpp"])
licant.module_defimpl("nos.error", "throw")

licant.module("nos",
	mdepends=[
		"nos.util",
		"nos.print",
		"nos.input",
		"nos.fprint",
		"nos.io",
#		"jackjack"
		
		"igris.include",
		"igris.bug",
		"igris.dprint",
	],
	include_paths=["."]
)

licant.module("nos.include",
	include_paths=["."]
)
