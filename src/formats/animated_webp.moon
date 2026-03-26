class AnimatedWebP extends Format
	new: =>
		@displayName = "WebP"
		@supportsTwopass = false
		@videoCodec = "libwebp_anim"
		@audioCodec = ""
		@outputExtension = "webp"
		@acceptsBitrate = false

	getFlags: =>
		{
			"--ovcopts-add=lossless=0",
			"--ovcopts-add=quality=#{options.animated_webp_quality}",
			"--ovcopts-add=compression_level=#{options.animated_webp_compression}",
		}

formats["animated-webp"] = AnimatedWebP!
