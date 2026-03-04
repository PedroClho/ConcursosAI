'use client';

import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

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
  green: '[&>div]:bg-green-600',
  blue: '[&>div]:bg-blue-600',
  purple: '[&>div]:bg-purple-600',
  orange: '[&>div]:bg-orange-600',
  yellow: '[&>div]:bg-yellow-600',
  red: '[&>div]:bg-red-600',
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
          {label && <span className="text-sm text-muted-foreground font-medium">{label}</span>}
          {showPercentage && (
            <span className="text-sm text-muted-foreground font-semibold">
              {percentage.toFixed(0)}%
            </span>
          )}
        </div>
      )}
      <Progress 
        value={percentage} 
        className={cn(heightClasses[size], colorClasses[color])}
      />
      {value !== undefined && max !== undefined && (
        <div className="flex items-center justify-between mt-1">
          <span className="text-xs text-muted-foreground">
            {value} / {max}
          </span>
        </div>
      )}
    </div>
  );
}
