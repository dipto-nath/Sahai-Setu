/**
 * Table component for SIH26093 Frontend
 */

import React from 'react';
import { cn } from '@/lib/utils';

export interface Column<T> {
  key: string;
  header: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

export interface TableProps<T> {
  columns?: Column<T>[];
  data?: T[];
  headers?: string[];
  rows?: React.ReactNode[][];
  keyExtractor?: (item: T) => string | number;
  className?: string;
  onRowClick?: (item: T) => void;
  emptyMessage?: string;
}

export function Table<T>({
  columns = [],
  data = [],
  headers,
  rows,
  keyExtractor,
  className,
  onRowClick,
  emptyMessage = 'No data available',
}: TableProps<T>) {
  // If raw headers and rows are passed
  if (headers && rows) {
    return (
      <div className={cn('overflow-x-auto rounded-lg border border-gray-200', className)}>
        {rows.length > 0 ? (
          <table className="w-full" role="table">
            <thead className="bg-gray-50">
              <tr>
                {headers.map((header, idx) => (
                  <th
                    key={idx}
                    scope="col"
                    className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {rows.map((row, rowIdx) => (
                <tr key={rowIdx} className="transition-colors hover:bg-gray-50">
                  {row.map((cell, cellIdx) => (
                    <td key={cellIdx} className="px-4 py-3 text-sm text-gray-900">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="p-8 text-center text-gray-500">{emptyMessage}</div>
        )}
      </div>
    );
  }

  const safeData = Array.isArray(data) ? data : [];
  const safeColumns = Array.isArray(columns) ? columns : [];

  return (
    <div className={cn('overflow-x-auto rounded-lg border border-gray-200', className)}>
      {safeData.length > 0 ? (
        <table className="w-full" role="table">
          <thead className="bg-gray-50">
            <tr>
              {safeColumns.map((column) => (
                <th
                  key={column.key}
                  scope="col"
                  className={cn(
                    'px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider',
                    column.className
                  )}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {safeData.map((item, index) => {
              const key = keyExtractor ? keyExtractor(item) : (item as any)?.id || index;
              return (
                <tr
                  key={key}
                  className={cn(
                    'transition-colors',
                    onRowClick && 'cursor-pointer hover:bg-gray-50'
                  )}
                  onClick={() => onRowClick?.(item)}
                >
                  {safeColumns.map((column) => (
                    <td
                      key={column.key}
                      className={cn('px-4 py-3 text-sm text-gray-900', column.className)}
                    >
                      {column.render ? column.render(item) : (item as any)[column.key]}
                    </td>
                  ))}
                </tr>
              );
            })}
          </tbody>
        </table>
      ) : (
        <div className="p-8 text-center text-gray-500">{emptyMessage}</div>
      )}
    </div>
  );
}
