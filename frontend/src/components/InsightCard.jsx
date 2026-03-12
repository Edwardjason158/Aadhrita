import { Sparkles } from 'lucide-react'

export default function InsightCard({ insight, suggestions }) {
  const suggestionList = Array.isArray(suggestions) 
    ? suggestions 
    : suggestions?.split(',').map(s => s.trim()) || []

  return (
    <div className="bg-white rounded-xl p-6 border border-slate-200">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="h-5 w-5 text-primary-600" />
        <h2 className="text-lg font-semibold text-slate-800">AI Insight</h2>
      </div>
      
      {insight ? (
        <>
          <p className="text-slate-600 mb-4 leading-relaxed">{insight}</p>
          
          {suggestionList.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-slate-700 mb-2">Suggestions:</h3>
              <ul className="space-y-2">
                {suggestionList.slice(0, 3).map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2 text-sm text-slate-600">
                    <span className="text-primary-600 font-semibold">{index + 1}.</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <p className="text-slate-500">
            Start tracking your health to get personalized AI insights!
          </p>
        </div>
      )}
    </div>
  )
}
