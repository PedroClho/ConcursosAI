'use client';

import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    value: number;
    direction: 'up' | 'down';
    label?: string;
  };
  color?: 'green' | 'blue' | 'purple' | 'orange' | 'yellow' | 'pink' | 'red';
  size?: 'sm' | 'md' | 'lg';
}

const colorClasses = {
  green: {
    bg: 'bg-green-600/20',
    text: 'text-green-400',
    border: 'border-green-500/30',
    trend: 'text-green-400',
  },
  blue: {
    bg: 'bg-blue-600/20',
    text: 'text-blue-400',
    border: 'border-blue-500/30',
    trend: 'text-blue-400',
  },
  purple: {
    bg: 'bg-purple-600/20',
    text: 'text-purple-400',
    border: 'border-purple-500/30',
    trend: 'text-purple-400',
  },
  orange: {
    bg: 'bg-orange-600/20',
    text: 'text-orange-400',
    border: 'border-orange-500/30',
    trend: 'text-orange-400',
  },
  yellow: {
    bg: 'bg-yellow-600/20',
    text: 'text-yellow-400',
    border: 'border-yellow-500/30',
    trend: 'text-yellow-400',
  },
  pink: {
    bg: 'bg-pink-600/20',
    text: 'text-pink-400',
    border: 'border-pink-500/30',
    trend: 'text-pink-400',
  },
  red: {
    bg: 'bg-red-600/20',
    text: 'text-red-400',
    border: 'border-red-500/30',
    trend: 'text-red-400',
  },
};

export default function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'green',
  size = 'md',
}: StatsCardProps) {
  const colors = colorClasses[color];
  
  const sizeClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const valueSizeClasses = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-4xl',
  };

  const iconSizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  return (
    <div
      className={`bg-gray-900 rounded-lg border ${colors.border} hover:border-opacity-50 transition-all shadow-lg hover:shadow-xl ${sizeClasses[size]}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <p className="text-gray-400 text-sm font-medium mb-1">{title}</p>
          <div className="flex items-baseline gap-2">
            <h3 className={`${colors.text} ${valueSizeClasses[size]} font-bold tracking-tight`}>
              {value}
            </h3>
            {trend && (
              <div
                className={`flex items-center gap-1 text-sm ${
                  trend.direction === 'up' ? 'text-green-400' : 'text-red-400'
                }`}
              >
                {trend.direction === 'up' ? (
                  <TrendingUp className="w-4 h-4" />
                ) : (
                  <TrendingDown className="w-4 h-4" />
                )}
                <span className="font-semibold">
                  {trend.value > 0 ? '+' : ''}
                  {trend.value}%
                </span>
              </div>
            )}
          </div>
          {subtitle && <p className="text-gray-500 text-xs mt-2">{subtitle}</p>}
          {trend?.label && (
            <p className="text-gray-600 text-xs mt-1">{trend.label}</p>
          )}
        </div>
        {Icon && (
          <div className={`${colors.bg} ${colors.text} p-3 rounded-lg`}>
            <Icon className={iconSizeClasses[size]} />
          </div>
        )}
      </div>
    </div>
  );
}
