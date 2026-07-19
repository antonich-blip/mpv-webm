class MainPage extends Page
	new: =>
		@keybinds =
			"c": self\crop
			"1": self\setStartTime
			"2": self\setEndTime
			"!": self\jumpToStartTime
			"@": self\jumpToEndTime
			"+": self\addSegment
			"-": self\clearSegments
			"o": self\changeOptions
			"p": self\preview
			"e": self\encode
			"ESC": self\hide
		@startTime = -1
		@endTime = -1
		@segments = {}
		@region = Region!

	setStartTime: =>
		@startTime = mp.get_property_number("time-pos")
		if @visible
			self\clear!
			self\draw!

	setEndTime: =>
		@endTime = mp.get_property_number("time-pos")
		if @visible
			self\clear!
			self\draw!

	jumpToStartTime: =>
		if @startTime < 0
			return
		mp.set_property("time-pos", @startTime)

	jumpToEndTime: =>
		if @endTime < 0
			return
		mp.set_property("time-pos", @endTime)

	addSegment: =>
		if @startTime < 0
			message("No start time, can't add section")
			return
		if @endTime < 0
			message("No end time, can't add section")
			return
		if @startTime >= @endTime
			message("Start time is ahead of end time, can't add section")
			return
		@segments[#@segments + 1] = {startTime: @startTime, endTime: @endTime}
		-- Reset the current selection, so the next section can be picked.
		@startTime = -1
		@endTime = -1
		if @visible
			self\clear!
			self\draw!

	clearSegments: =>
		self\setupStartAndEndTimes!

	setupStartAndEndTimes: =>
		@segments = {}
		if mp.get_property_native("duration")
			-- Note: there exists an option called rebase-start-time, which, when set to no,
			-- could cause the beginning of the video to not be at 0. Not sure how this
			-- would affect this code.
			@startTime = 0
			@endTime = mp.get_property_native("duration")
		else
			@startTime = -1
			@endTime = -1
		
		if @visible
			self\clear!
			self\draw!

	draw: =>
		window_w, window_h = mp.get_osd_size()
		ass = assdraw.ass_new()
		ass\new_event()
		self\setup_text(ass)
		ass\append("#{bold('WebM maker')}\\N\\N")
		ass\append("#{bold('c:')} crop\\N")
		ass\append("#{bold('1:')} set start time (current is #{seconds_to_time_string(@startTime)})\\N")
		ass\append("#{bold('2:')} set end time (current is #{seconds_to_time_string(@endTime)})\\N")
		ass\append("#{bold('!:')} jump to start time\\N")
		ass\append("#{bold('@:')} jump to end time\\N")
		ass\append("#{bold('+:')} add current times as a section\\N")
		ass\append("#{bold('-:')} clear all sections\\N")
		if #@segments > 0
			section_strings = ["#{seconds_to_time_string(s.startTime)} - #{seconds_to_time_string(s.endTime)}" for s in *@segments]
			ass\append("#{bold('sections:')} #{table.concat(section_strings, ", ")}\\N")
		ass\append("#{bold('o:')} change encode options\\N")
		ass\append("#{bold('p:')} preview\\N")
		ass\append("#{bold('e:')} encode\\N\\N")
		ass\append("#{bold('ESC:')} close\\N")
		mp.set_osd_ass(window_w, window_h, ass.text)
	
	show: =>
		super\show!

		emit_event("show-main-page")

	onUpdateCropRegion: (updated, newRegion) =>
		if updated
			@region = newRegion
		self\show!

	crop: =>
		self\hide!
		cropPage = CropPage(self\onUpdateCropRegion, @region)
		cropPage\show!

	onOptionsChanged: (updated) =>
		self\show!

	changeOptions: =>
		self\hide!
		encodeOptsPage = EncodeOptionsPage(self\onOptionsChanged)
		encodeOptsPage\show!

	onPreviewEnded: =>
		self\show!

	preview: =>
		self\hide!
		previewPage = PreviewPage(self\onPreviewEnded, @region, @startTime, @endTime)
		previewPage\show!

	encode: =>
		self\hide!
		segments = [s for s in *@segments]
		-- Include the current selection as the last section, when valid.
		if @startTime >= 0 and @endTime >= 0 and @startTime < @endTime
			segments[#segments + 1] = {startTime: @startTime, endTime: @endTime}
		if #segments == 0
			if @startTime < 0
				message("No start time, aborting")
				return
			if @endTime < 0
				message("No end time, aborting")
				return
			message("Start time is ahead of end time, aborting")
			return
		encode(@region, segments)
