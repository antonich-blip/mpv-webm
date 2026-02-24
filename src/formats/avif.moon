class AVIF extends Format
	new: =>
		@displayName = "AVIF"
		@supportsTwopass = false
		@videoCodec = "libsvtav1"
		@audioCodec = ""
		@outputExtension = "avif"
		@acceptsBitrate = false

	getFlags: =>
		crf = options.avif_crf
		compression = options.avif_compression
		{
			"--ovcopts-add=crf=#{crf}",
			"--ovcopts-add=preset=#{compression}",
			"--ovcopts=svtav1-params=tune=1:keyint=240"
		}

formats["avif"] = AVIF!
