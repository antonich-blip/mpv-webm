-- Cuts the source without re-encoding, by running ffmpeg with stream copy
-- instead of mpv. Nothing can be filtered (no crop, scale, fps...), and the
-- cut starts at the keyframe preceding the start time.
class Copy extends Format
	new: =>
		@displayName = "Copy (no re-encode)"
		@supportsTwopass = false
		@videoCodec = ""
		@audioCodec = ""
		-- Set per encode, from options.copy_extension or the source file.
		@outputExtension = ""
		@acceptsBitrate = false
		@streamCopy = true

formats["copy"] = Copy!

