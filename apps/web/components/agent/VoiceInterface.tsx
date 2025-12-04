'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'

interface VoiceInterfaceProps {
  onTranscript: (text: string) => void
  onAgentResponse?: (text: string) => void
  isListening: boolean
  setIsListening: (listening: boolean) => void
  voiceEnabled?: boolean
  setVoiceEnabled?: (enabled: boolean) => void
}

export function VoiceInterface({
  onTranscript,
  onAgentResponse,
  isListening,
  setIsListening,
  voiceEnabled = true,
  setVoiceEnabled
}: VoiceInterfaceProps) {
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isSupported, setIsSupported] = useState(false)
  const recognitionRef = useRef<any>(null)
  const synthesisRef = useRef<SpeechSynthesis | null>(null)

  useEffect(() => {
    // Check browser support
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    setIsSupported(!!SpeechRecognition && 'speechSynthesis' in window)

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition()
      recognition.continuous = false
      recognition.interimResults = false
      recognition.lang = 'en-US'

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        onTranscript(transcript)
        setIsListening(false)
      }

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
      }

      recognition.onend = () => {
        setIsListening(false)
      }

      recognitionRef.current = recognition
    }

    synthesisRef.current = window.speechSynthesis
  }, [onTranscript])

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start()
        setIsListening(true)
      } catch (error) {
        console.error('Error starting speech recognition:', error)
      }
    }
  }

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop()
      setIsListening(false)
    }
  }

  const speak = (text: string) => {
    if (synthesisRef.current) {
      // Stop any ongoing speech
      synthesisRef.current.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      utterance.rate = 0.9
      utterance.pitch = 1
      utterance.volume = 1

      utterance.onstart = () => setIsSpeaking(true)
      utterance.onend = () => setIsSpeaking(false)
      utterance.onerror = () => setIsSpeaking(false)

      synthesisRef.current.speak(utterance)
    }
  }

  const stopSpeaking = () => {
    if (synthesisRef.current) {
      synthesisRef.current.cancel()
      setIsSpeaking(false)
    }
  }


  if (!isSupported) {
    return (
      <Card className="border-yellow-200 bg-yellow-50">
        <CardContent className="p-4">
          <p className="text-sm text-yellow-800">
            Voice features require a modern browser with speech recognition support (Chrome, Edge, Safari).
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="flex items-center gap-2">
      {/* Voice Input */}
      <Button
        variant={isListening ? "default" : "outline"}
        size="sm"
        onClick={isListening ? stopListening : startListening}
        className={isListening ? "bg-red-500 hover:bg-red-600 text-white animate-pulse" : ""}
        title={isListening ? "Stop listening" : "Start voice input"}
      >
        {isListening ? (
          <>
            <MicOff className="h-4 w-4 mr-2" />
            Listening...
          </>
        ) : (
          <>
            <Mic className="h-4 w-4 mr-2" />
            Voice
          </>
        )}
      </Button>

      {/* Voice Output Toggle */}
      {setVoiceEnabled && (
        <Button
          variant={voiceEnabled ? "default" : "outline"}
          size="sm"
          onClick={() => {
            if (isSpeaking) {
              stopSpeaking()
            }
            setVoiceEnabled(!voiceEnabled)
          }}
          className={voiceEnabled ? "bg-green-500 hover:bg-green-600 text-white" : ""}
          title={voiceEnabled ? "Disable voice output" : "Enable voice output"}
        >
          {voiceEnabled ? (
            <Volume2 className="h-4 w-4" />
          ) : (
            <VolumeX className="h-4 w-4" />
          )}
        </Button>
      )}

      {/* Stop Speaking Button */}
      {isSpeaking && (
        <Button
          variant="outline"
          size="sm"
          onClick={stopSpeaking}
          className="text-blue-600"
          title="Stop speaking"
        >
          <VolumeX className="h-4 w-4 mr-2" />
          Stop
        </Button>
      )}
    </div>
  )
}

// Export speak function for use in parent
export const speakText = (text: string) => {
  if ('speechSynthesis' in window) {
    const synthesis = window.speechSynthesis
    synthesis.cancel() // Stop any ongoing speech

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.rate = 0.9
    utterance.pitch = 1
    utterance.volume = 1

    synthesis.speak(utterance)
    return synthesis
  }
  return null
}

