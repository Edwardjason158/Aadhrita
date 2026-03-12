export default function HealthMetricCard({ label, value, unit, icon, good }) {
  return (
    <div className="bg-white rounded-xl p-4 border border-slate-200">
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        {good !== undefined && (
          <span
            className={`text-xs font-medium px-2 py-1 rounded-full ${
              good
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            {good ? 'Good' : 'Low'}
          </span>
        )}
      </div>
      <div className="text-sm text-slate-500 mb-1">{label}</div>
      <div className="text-2xl font-bold text-slate-800">
        {value !== undefined && value !== null ? (
          <>
            {value}
            <span className="text-sm font-normal text-slate-500 ml-1">{unit}</span>
          </>
        ) : (
          <span className="text-sm font-normal text-slate-400">No data</span>
        )}
      </div>
    </div>
  )
}
