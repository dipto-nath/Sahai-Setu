/**
 * Button component for SIH26093 Frontend
 */

import React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive';
type ButtonSize = 'sm' | 'md' | 'lg';

interface BaseProps {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  className?: string;
  children?: React.ReactNode;
}

type ButtonAsButton = BaseProps & 
  Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, keyof BaseProps> & {
    href?: undefined;
  };

type ButtonAsLink = BaseProps & {
  href: string;
  target?: string;
  rel?: string;
  onClick?: (e: React.MouseEvent<HTMLAnchorElement>) => void;
  type?: never;
  disabled?: boolean;
};

type ButtonProps = ButtonAsButton | ButtonAsLink;

const baseStyles = 'inline-flex items-center justify-center font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none rounded-lg';

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700',
  secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200',
  outline: 'border border-gray-300 bg-transparent hover:bg-gray-50',
  ghost: 'bg-transparent hover:bg-gray-100',
  destructive: 'bg-red-600 text-white hover:bg-red-700',
};

const sizes: Record<ButtonSize, string> = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-4 py-2 text-sm',
  lg: 'h-12 px-6 text-base',
};

function renderLoading() {
  return (
    <svg
      className="mr-2 h-4 w-4 animate-spin"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (props, ref) => {
    const {
      className,
      variant = 'primary',
      size = 'md',
      isLoading,
      children,
      disabled,
      ...rest
    } = props as ButtonAsButton & Partial<ButtonAsLink>;

    const classes = cn(baseStyles, variants[variant], sizes[size], className);

    if ('href' in rest && rest.href) {
      const { href, target, rel, onClick } = rest as unknown as ButtonAsLink;
      return (
        <Link
          href={href}
          target={target}
          rel={rel}
          onClick={onClick}
          className={classes}
          aria-disabled={disabled || isLoading}
        >
          {isLoading && renderLoading()}
          {children}
        </Link>
      );
    }

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || isLoading}
        {...(rest as React.ButtonHTMLAttributes<HTMLButtonElement>)}
      >
        {isLoading && renderLoading()}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
