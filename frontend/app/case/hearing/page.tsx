import StepBar from '@/components/StepBar'
import HearingTranscript from './Transcript'

export default function HearingPage() {
  return (
    <div className="max-w-3xl">
      <StepBar />
      <p className="text-sm text-gray-500 mb-6">
        Virtual hearing transcript linked to the case record.
      </p>
      <HearingTranscript />
    </div>
  )
}
