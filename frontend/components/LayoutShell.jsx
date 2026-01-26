import React from 'react';
import Sidebar from '@/components/Sidebar';

/**
 * LayoutShell: Shared shell to keep a consistent gray theme and sidebar across pages.
 * Props:
 *  - children: page content
 *  - sidebarProps: props forwarded to Sidebar (user, conversations, handlers)
 *  - header: optional header node rendered above content
 */
export default function LayoutShell({ children, sidebarProps = {}, header = null }) {
  return (
    <div className="min-h-screen flex bg-[#f5f6f8] text-slate-900 overflow-hidden">
      <Sidebar {...sidebarProps} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {header}
        <div className="flex-1 flex flex-col overflow-y-auto">{children}</div>
      </div>
    </div>
  );
}
