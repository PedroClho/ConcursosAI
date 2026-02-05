'use client';

import { CheckCircle, XCircle } from 'lucide-react';

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

        let className =
          'border-2 rounded-lg p-4 transition-all duration-200 ';

        if (disabled) {
          className += 'cursor-default ';
        } else {
          className += 'cursor-pointer hover:bg-gray-800/50 ';
        }

        if (isCorrect) {
          className += 'border-green-500 bg-green-500/10 shadow-lg shadow-green-500/20';
        } else if (isIncorrect) {
          className += 'border-red-500 bg-red-500/10 shadow-lg shadow-red-500/20';
        } else if (isSelected) {
          className += 'border-green-500 bg-green-500/5';
        } else {
          className += 'border-gray-700 hover:border-gray-600';
        }

        return (
          <div
            key={option.value}
            onClick={() => !disabled && onChange(option.value)}
            className={className}
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
                  className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
                    isSelected
                      ? 'border-green-500 bg-green-500'
                      : 'border-gray-600 bg-gray-800'
                  }`}
                >
                  {isSelected && (
                    <div className="w-2 h-2 rounded-full bg-white"></div>
                  )}
                </div>
              </div>

              {/* Label */}
              <div className="flex-1 flex items-start gap-3">
                <span className="font-bold text-gray-400 flex-shrink-0 min-w-[2rem]">
                  {option.value})
                </span>
                <span
                  className={`flex-1 ${
                    isCorrect
                      ? 'text-green-300 font-medium'
                      : isIncorrect
                      ? 'text-red-300'
                      : 'text-gray-300'
                  }`}
                >
                  {option.label}
                </span>
              </div>

              {/* Status Icon */}
              <div className="flex-shrink-0">
                {isCorrect && <CheckCircle className="w-5 h-5 text-green-500" />}
                {isIncorrect && <XCircle className="w-5 h-5 text-red-500" />}
              </div>
            </label>
          </div>
        );
      })}
    </div>
  );
}
