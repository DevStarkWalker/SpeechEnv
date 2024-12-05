while ($true) {
    $currentTime = (Get-Date).ToString("HH:mm")
    if ($currentTime -eq "05:30") {
        Start-Process -FilePath "python" -ArgumentList "main.py" -WorkingDirectory "D:\Projects\SpeechAssistant\SpeechEnv\voice_assistant"
        Start-Sleep -Seconds 60  # Wait 60 seconds to avoid reruns in the same minute
	"Script triggered at $currentTime" | Out-File -FilePath "D:\Projects\SpeechAssistant\SpeechEnv\voice_assistant\log.txt" -Append

    }
    Start-Sleep -Seconds 30  # Check time every 30 seconds
}

