class AVIF extends Format
	new: =>
		@displayName = "AVIF"
		@supportsTwopass = false
		@videoCodec = "libsvtav1"
		@audioCodec = ""
		@outputExtension = "avif"
		@acceptsBitrate = false

	-- Default to 60fps for animated AVIF output. The global fps filter is
	-- chained after this one in get_video_filters, so a user-set options.fps
	-- still wins (the later fps filter in the chain dictates output rate).
	getPreFilters: =>
		if options.fps <= 0
			return {"fps=60"}
		return {}

	getFlags: =>
		crf = options.avif_crf
		compression = options.avif_compression
		{
			"--ovcopts-add=crf=#{crf}",
			"--ovcopts-add=preset=#{compression}",
			-- tune=0 optimizes for visual quality rather than PSNR.
			"--ovcopts-add=svtav1-params=tune=0:keyint=240"
		}

formats["avif"] = AVIF!
