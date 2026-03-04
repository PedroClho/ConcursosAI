'use client';

import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

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
    bg: 'bg-green-500/10',
    text: 'text-green-600 dark:text-green-400',
    border: 'border-green-500/20',
  },
  blue: {
    bg: 'bg-blue-500/10',
    text: 'text-blue-600 dark:text-blue-400',
    border: 'border-blue-500/20',
  },
  purple: {
    bg: 'bg-purple-500/10',
    text: 'text-purple-600 dark:text-purple-400',
    border: 'border-purple-500/20',
  },
  orange: {
    bg: 'bg-orange-500/10',
    text: 'text-orange-600 dark:text-orange-400',
    border: 'border-orange-500/20',
  },
  yellow: {
    bg: 'bg-yellow-500/10',
    text: 'text-yellow-600 dark:text-yellow-400',
    border: 'border-yellow-500/20',
  },
  pink: {
    bg: 'bg-pink-500/10',
    text: 'text-pink-600 dark:text-pink-400',
    border: 'border-pink-500/20',
  },
  red: {
    bg: 'bg-red-500/10',
    text: 'text-red-600 dark:text-red-400',
    border: 'border-red-500/20',
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
    <Card className={cn('border', colors.border, sizeClasses[size])}>
      <CardContent className="p-0">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-muted-foreground text-sm font-medium mb-1">{title}</p>
            <div className="flex items-baseline gap-2">
              <h3 className={cn(colors.text, valueSizeClasses[size], 'font-bold tracking-tight')}>
                {value}
              </h3>
              {trend && (
                <div
                  className={cn(
                    'flex items-center gap-1 text-sm',
                    trend.direction === 'up' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                  )}
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
            {subtitle && <p className="text-muted-foreground text-xs mt-2">{subtitle}</p>}
            {trend?.label && (
              <p className="text-muted-foreground text-xs mt-1">{trend.label}</p>
            )}
          </div>
          {Icon && (
            <div className={cn(colors.bg, colors.text, 'p-3 rounded-lg')}>
              <Icon className={iconSizeClasses[size]} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
