'use client';

interface ProgressBarProps {
  value: number;
  max?: number;
  label?: string;
  showPercentage?: boolean;
  color?: 'green' | 'blue' | 'purple' | 'orange' | 'yellow' | 'red';
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

const colorClasses = {
  green: 'bg-green-600',
  blue: 'bg-blue-600',
  purple: 'bg-purple-600',
  orange: 'bg-orange-600',
  yellow: 'bg-yellow-600',
  red: 'bg-red-600',
};

export default function ProgressBar({
  value,
  max = 100,
  label,
  showPercentage = true,
  color = 'green',
  size = 'md',
  animated = true,
}: ProgressBarProps) {
  const percentage = Math.min((value / max) * 100, 100);
  
  const heightClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
  };

  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex items-center justify-between mb-2">
          {label && <span className="text-sm text-gray-400 font-medium">{label}</span>}
          {showPercentage && (
            <span className="text-sm text-gray-400 font-semibold">
              {percentage.toFixed(0)}%
            </span>
          )}
        </div>
      )}
      <div className={`w-full bg-gray-800 rounded-full overflow-hidden ${heightClasses[size]}`}>
        <div
          className={`${colorClasses[color]} ${heightClasses[size]} rounded-full transition-all duration-500 ease-out ${
            animated ? 'animate-pulse-subtle' : ''
          }`}
          style={{ width: `${percentage}%` }}
        >
          {animated && (
            <div className="h-full w-full bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
          )}
        </div>
      </div>
      {value !== undefined && max !== undefined && (
        <div className="flex items-center justify-between mt-1">
          <span className="text-xs text-gray-600">
            {value} / {max}
          </span>
        </div>
      )}
    </div>
  );
}
