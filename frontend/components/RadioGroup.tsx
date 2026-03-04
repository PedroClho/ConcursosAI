'use client';

import { CheckCircle, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface RadioOption {
  value: string;
  label: string;
}

interface RadioGroupProps {
  options: RadioOption[];
  value?: string;
  onChange: (value: string) => void;
  disabled?: boolean;
  correctValue?: string;
  name?: string;
}

export default function RadioGroup({
  options,
  value,
  onChange,
  disabled = false,
  correctValue,
  name = 'radio-group',
}: RadioGroupProps) {
  return (
    <div className="space-y-3">
      {options.map((option) => {
        const isSelected = value === option.value;
        const isCorrect = correctValue && option.value === correctValue;
        const isIncorrect = correctValue && isSelected && option.value !== correctValue;

        return (
          <div
            key={option.value}
            onClick={() => !disabled && onChange(option.value)}
            className={cn(
              'border-2 rounded-lg p-4 transition-all duration-200',
              disabled ? 'cursor-default' : 'cursor-pointer hover:bg-accent/50',
              isCorrect && 'border-primary bg-primary/10 shadow-lg',
              isIncorrect && 'border-destructive bg-destructive/10 shadow-lg',
              !isCorrect && !isIncorrect && isSelected && 'border-primary bg-primary/5',
              !isCorrect && !isIncorrect && !isSelected && 'border-border hover:border-primary/50'
            )}
          >
            <label className="flex items-center gap-4 cursor-pointer">
              {/* Radio Button Visual */}
              <div className="flex-shrink-0 relative">
                <input
                  type="radio"
                  name={name}
                  value={option.value}
                  checked={isSelected}
                  onChange={() => !disabled && onChange(option.value)}
                  disabled={disabled}
                  className="sr-only"
                />
                <div
                  className={cn(
                    'w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all',
                    isSelected
                      ? 'border-primary bg-primary'
                      : 'border-muted-foreground bg-background'
                  )}
                >
                  {isSelected && (
                    <div className="w-2 h-2 rounded-full bg-primary-foreground"></div>
                  )}
                </div>
              </div>

              {/* Label */}
              <div className="flex-1 flex items-start gap-3">
                <span className="font-bold text-muted-foreground flex-shrink-0 min-w-[2rem]">
                  {option.value})
                </span>
                <span
                  className={cn(
                    'flex-1',
                    isCorrect && 'text-primary font-medium',
                    isIncorrect && 'text-destructive',
                    !isCorrect && !isIncorrect && 'text-foreground'
                  )}
                >
                  {option.label}
                </span>
              </div>

              {/* Status Icon */}
              <div className="flex-shrink-0">
                {isCorrect && <CheckCircle className="w-5 h-5 text-primary" />}
                {isIncorrect && <XCircle className="w-5 h-5 text-destructive" />}
              </div>
            </label>
          </div>
        );
      })}
    </div>
  );
}
