

	songCandidatesList = getTop50()
	completedSongsURLs = {}
	songDatabase = []

	while completedSongs.length < 5000 :

		currentSong = []
		currentSong.append( songCandidatesList.pop() )
		currentPageHTML = getPageFromURL( currentSong )

		currentSong.